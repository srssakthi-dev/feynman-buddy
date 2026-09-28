import { useEffect, useRef, useState } from 'react'
import { request } from './api'
import SpeechInput from './SpeechInput'
import BuddyPlayback from './BuddyPlayback'
import DiagramPractice from './DiagramPractice'
import TopicFigures from './TopicFigures'

export default function StudySession({ session }) {
  const [study, setStudy] = useState(null)
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState('Loading your session…')
  const [error, setError] = useState('')
  const [audioActive, setAudioActive] = useState(false)
  const [transcriptionId, setTranscriptionId] = useState(null)
  const pending = useRef(null)
  const latest = useRef(null)
  const base = `/sessions/${session.id}`
  const turns = study?.messages.filter(message => message.role === 'student').length || 0
  const activeFigure = study?.figures?.find(figure => figure.id === study.active_figure_id)

  async function load() {
    setBusy('Loading your session…')
    setError('')
    try { setStudy(await request(`${base}/study`)) }
    catch (failure) { setError(failure.message === 'Not Found' ? 'Please restart the backend to load the new upload and conversation features.' : failure.message) }
    finally { setBusy('') }
  }

  useEffect(() => { load() }, [session.id])
  useEffect(() => {
    if (study?.messages.length) latest.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [study?.messages.length])

  async function action(path, label, options = {}) {
    setBusy(label)
    setError('')
    try {
      const next = await request(`${base}${path}`, { method: 'POST', ...options })
      setStudy(next)
      return true
    } catch (failure) {
      setError(failure.message)
      return false
    } finally { setBusy('') }
  }

  async function upload(event) {
    event.preventDefault()
    if (!file || busy) return
    if (file.size > 10 * 1024 * 1024) { setError('Choose a PDF smaller than 10 MB.'); return }
    const body = new FormData()
    body.append('file', file)
    if (await action('/documents', 'Reading and preparing your notes… The first upload may take a little longer.', { body })) setFile(null)
  }

  async function send(event) {
    event.preventDefault()
    if (!text.trim() || busy || audioActive) return
    const value = text.trim()
    if (!pending.current || pending.current.text !== value || pending.current.transcription_id !== transcriptionId) pending.current = { text: value, request_id: crypto.randomUUID(), transcription_id: transcriptionId }
    if (await action('/turn', 'Your buddy is thinking… The local model may take a little time.', {
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(pending.current),
    })) { setText(''); setTranscriptionId(null); pending.current = null }
  }

  async function download() {
    setError('')
    try {
      const data = await request(`${base}/export`)
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
      const link = document.createElement('a')
      link.href = url; link.download = 'explaino-practice.json'; link.click()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (failure) { setError(failure.message) }
  }

  return <div className="practice-space">
    {error && <div className="error" role="alert">{error}{!study && <button className="text-button" onClick={load} disabled={!!busy}>Retry</button>}</div>}
    {busy && <p className="working-status" role="status">{busy}</p>}
    {study && <>
      <section className="notes-card" aria-labelledby="notes-title">
        <div className="notes-heading"><div><p className="eyebrow">YOUR SOURCE MATERIAL</p><h2 id="notes-title">Your notes</h2></div>{study.document && <span className="ready-badge">Ready to practise</span>}</div>
        {!study.document ? <form onSubmit={upload} className="upload-form">
          <p>Upload a PDF about {session.name}. No special headings or template needed.</p>
          <label htmlFor="notes-file">Choose your PDF</label>
          <input id="notes-file" type="file" accept=".pdf,application/pdf" onChange={event => { setFile(event.target.files[0] || null); setError('') }} disabled={!!busy} />
          <p className="file-guidance">Selectable-text PDF · up to 20 pages · 10 MB. After uploading, you can add selected figures to this conversation.</p>
          <button className="primary compact" disabled={!file || !!busy}>Upload and prepare notes</button>
        </form> : <>
          <p className="document-name">{study.document.filename} <span>· {study.document.page_count} pages</span></p>
          <a className="source-link" href={`/api${base}/notes.pdf`} target="_blank" rel="noreferrer">Open original PDF ↗</a>
          {study.document.warnings.map(warning => <p className="extraction-warning" key={warning}>{warning}</p>)}
          <details className="source-preview"><summary>Check the text read from your notes</summary>
            <p>These are source passages for your buddy, not a checklist you need to answer. Check that the text was read correctly before starting.</p>
            {study.document.chunks.map(chunk => <article key={chunk.id}><a href={`/api${base}/notes.pdf#page=${chunk.page}`} target="_blank" rel="noreferrer">Page {chunk.page}</a><p>{chunk.text}</p></article>)}
          </details>
        </>}
      </section>

      {study.document && !study.diagram && <TopicFigures base={base} study={study} busy={!!busy || audioActive} setBusy={setBusy} setStudy={setStudy} />}
      {study.document && study.diagram && <DiagramPractice base={base} study={study} busy={!!busy || audioActive} setStudy={setStudy} />}
      {study.document && <section className="conversation-card" aria-labelledby="conversation-title">
        <div className="notes-heading"><div><p className="eyebrow">LEARN BY TEACHING</p><h2 id="conversation-title">Teach your buddy</h2></div>{study.started && <span className="turn-count">{turns} / 8 responses</span>}</div>
        {!study.started ? <>
          <p className="conversation-intro">{study.diagram ? 'Explain this diagram in your own words. Your buddy receives the saved description and relevant notes to follow along.' : 'Explain the idea as if your buddy is learning it for the first time. It will use your notes to follow along and ask questions.'}</p>
          <button className="primary compact" disabled={!!busy || !!(study.diagram && !study.diagram.approved_caption)} onClick={() => action('/start', 'Opening your practice…')}>{study.diagram ? 'Start diagram practice' : 'Start explaining'}</button>
        </> : <>
          {activeFigure && <aside className="active-figure-context" aria-label="Figure currently being discussed">
            <a href={`/api${base}/figures/${activeFigure.id}/image.png`} target="_blank" rel="noreferrer">
              <img src={`/api${base}/figures/${activeFigure.id}/image.png`} alt={`Figure from page ${activeFigure.page}`} />
            </a>
            <div><strong>Discussing the figure on page {activeFigure.page}</strong>
              <p>What do you notice in this figure, and how does it connect to what you just explained? Your buddy uses its reviewed description and relevant notes; it cannot check visual details on its own.</p>
              <button className="text-button" disabled={!!busy || audioActive}
                onClick={() => action('/figures/return-to-topic', 'Returning to your topic…')}>Return to the topic</button>
            </div>
          </aside>}
          <div className="conversation-log" aria-live="polite">
            {study.messages.map(message => <article key={message.id} className={`message ${message.role}`}>
              <strong>{message.role === 'buddy' ? 'Your buddy' : 'You'}</strong><p>{message.text}</p>
              {message.role === 'buddy' && study.reply_sources?.[message.id] && <details className="reply-sources">
                <summary>Notes supplied for this reply</summary>
                <p className="source-context-note">These passages were sent to the buddy. They do not prove that every statement in its reply is supported by your notes.</p>
                {study.reply_sources[message.id].length === 0 ? <p>No source passages were recorded for this reply.</p>
                  : study.reply_sources[message.id].map(source => <div className="reply-source" key={source.id}>
                    <a className="source-link" href={`/api${base}/notes.pdf#page=${source.page}`} target="_blank" rel="noreferrer">Page {source.page} ↗</a>
                    {source.kind === 'reviewed_figure_description' && <a className="source-link" href={`/api${base}/figures/${source.id.slice(7)}/image.png`} target="_blank" rel="noreferrer">View the figure ↗</a>}
                    {source.kind === 'reviewed_diagram_description' && <small>Reviewed AI diagram description · not independently verified</small>}
                    {source.kind === 'reviewed_figure_description' && <small>Reviewed BLIP description · not independently verified</small>}
                    <blockquote>{source.text}</blockquote>
                  </div>)}
              </details>}
            </article>)}
            <div ref={latest} />
          </div>
          <BuddyPlayback messages={study.messages} blocked={audioActive || !!busy} />
          {!study.finished && <>
            {turns < 8 ? <form onSubmit={send} className="reply-form">
              <SpeechInput base={base} disabled={!!busy} onActive={setAudioActive}
                onUse={(value, id) => { setText(value); setTranscriptionId(id) }} />
              <label htmlFor="explanation">Your explanation</label>
              <textarea id="explanation" value={text} onChange={event => setText(event.target.value)} maxLength={1200} rows={4} placeholder="Explain the idea in your own words…" disabled={!!busy} />
              <div className="reply-actions"><small>Type or review a recorded explanation, then send.</small><button className="primary compact" disabled={!text.trim() || !!busy || audioActive}>{busy ? 'Waiting for your buddy…' : 'Send explanation'}</button></div>
            </form> : <p className="notice">You have reached eight responses. Finish this short practice and reflect.</p>}
            <button className="secondary" disabled={!turns || !!busy || audioActive} onClick={() => action('/finish', 'Reviewing your conversation against the notes…')}>{busy.startsWith('Reviewing') ? 'Preparing reflection…' : 'Finish and reflect'}</button>
          </>}
          <button className="text-button" onClick={download} disabled={!!busy}>Download conversation and evidence</button>
        </>}
      </section>}

      {study.reflection && <section className="reflection-card" aria-labelledby="reflection-title">
        <p className="eyebrow">REFLECT & REVISIT</p><h2 id="reflection-title">Your practice reflection</h2>
        {study.diagram && <p className="source-context-note">This reflection uses your reviewed AI description and notes. The conversation model has not independently checked the image.</p>}
        {!study.diagram && study.figures?.length > 0 && <p className="source-context-note">Figure observations rely on your explanations, reviewed BLIP descriptions and notes. The buddy has not independently checked the image.</p>}
        <p className="reflection-summary">{study.reflection.trace?.prompt_version === 'reflection-v2'
          ? study.reflection.summary
          : 'This reflection was generated with an earlier prompt. Its observations may be unreliable; start a new practice to use the revised reflection. The original result remains in your downloaded evidence.'}</p>
        <div><h3>What came up in this practice</h3>
          {[...study.reflection.explained, ...study.reflection.revisit].length === 0 ? <p className="muted">No source-linked observation was recorded. That is not a judgement of your knowledge.</p> : [...study.reflection.explained, ...study.reflection.revisit].map((item, index) => <article className="reflection-item" key={index}>
            <p>{item.observation}</p>
            <details><summary>See your explanation and source</summary>{item.evidence.map(evidence => <blockquote key={evidence.id}>{evidence.text}</blockquote>)}
              <p className="source-context-note">Compare the observation with the actual passage; a page link alone does not verify it.</p>
              {item.sources.map(source => <div key={source.id}><a className="source-link" href={`/api${base}/notes.pdf#page=${source.page}`} target="_blank" rel="noreferrer">Revisit page {source.page} ↗</a><blockquote>{source.text}</blockquote></div>)}
            </details>
          </article>)}
        </div>
        <p className="reflection-disclaimer">{study.reflection.limitations} {study.reflection.warning}</p>
      </section>}
    </>}
  </div>
}

import { useRef, useState } from 'react'
import { request } from './api'

function FigureCard({ figure, base, study, setStudy, busy, setBusy }) {
  const [caption, setCaption] = useState(figure.reviewed_caption ?? figure.original_caption)
  const [error, setError] = useState('')
  const [dirty, setDirty] = useState(false)
  const active = study.active_figure_id === figure.id
  const alreadyUsed = study.reply_sources && Object.values(study.reply_sources).some(
    sources => sources.some(source => source.id === `FIGURE-${figure.id}`))

  async function action(path, label, body) {
    setBusy(label); setError('')
    try {
      const next = await request(path, { method: 'POST', ...(body ? {
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      } : {}) })
      setStudy(next); setDirty(false)
    } catch (failure) { setError(failure.message) }
    finally { setBusy('') }
  }

  return <article className="figure-card">
    <h3>Figure on page {figure.page}{active ? ' · Discussing now' : ''}</h3>
    <a href={`/api${base}/figures/${figure.id}/image.png`} target="_blank" rel="noreferrer">
      <img className="diagram-image" src={`/api${base}/figures/${figure.id}/image.png`} alt={`Figure selected from page ${figure.page}`} />
    </a>
    <a className="source-link" href={`/api${base}/notes.pdf#page=${figure.page}`} target="_blank" rel="noreferrer">Open source page {figure.page} ↗</a>
    {figure.printed_caption && <p><strong>Printed caption you supplied:</strong> {figure.printed_caption}</p>}
    <p className="source-context-note">BLIP's image description is a starting cue, not a checked interpretation. Compare it with the displayed figure and correct it before discussion.</p>
    <label htmlFor={`figure-caption-${figure.id}`}>Reviewed description</label>
    <textarea id={`figure-caption-${figure.id}`} rows={4} value={caption} maxLength={4000}
      disabled={!!busy || active || alreadyUsed}
      onChange={event => { setCaption(event.target.value); setDirty(true) }} />
    {!active && !alreadyUsed && <button className="secondary" disabled={!!busy || !caption.trim()}
      onClick={() => action(`${base}/figures/${figure.id}/review`, 'Saving the figure description…', { text: caption })}>
      {dirty ? 'Save corrected description' : 'Save reviewed description'}</button>}
    <details className="source-preview"><summary>Original BLIP caption and timing</summary>
      <p>{figure.original_caption}</p><small>{figure.trace.model} · {figure.trace.wall_seconds} seconds{figure.edited ? ' · corrected during review' : ''}</small>
    </details>
    {study.started && !study.finished && !active && <button className="secondary"
      disabled={!!busy || !figure.reviewed_caption || dirty}
      onClick={() => action(`${base}/figures/${figure.id}/discuss`, 'Bringing the figure into your conversation…')}>
      Discuss this figure with your buddy</button>}
    {active && study.started && !study.finished && <button className="secondary" disabled={!!busy}
      onClick={() => action(`${base}/figures/return-to-topic`, 'Returning to your topic…')}>Return to the topic</button>}
    {error && <p className="error" role="alert">{error}</p>}
  </article>
}

export default function TopicFigures({ base, study, setStudy, busy, setBusy }) {
  const [file, setFile] = useState(null)
  const [page, setPage] = useState(1)
  const [printed, setPrinted] = useState('')
  const [error, setError] = useState('')
  const retryId = useRef(null)
  const figures = study.figures ?? []

  async function upload(event) {
    event.preventDefault()
    if (!file || busy) return
    if (file.size > 8 * 1024 * 1024) { setError('Choose a PNG or JPEG under 8 MB.'); return }
    retryId.current ||= crypto.randomUUID()
    const body = new FormData()
    body.append('file', file); body.append('page', page)
    body.append('printed_caption', printed.trim()); body.append('request_id', retryId.current)
    setBusy('BLIP is describing your figure…'); setError('')
    try {
      setStudy(await request(`${base}/figures`, { method: 'POST', body }))
      setFile(null); setPrinted(''); retryId.current = null
    } catch (failure) { setError(failure.message) }
    finally { setBusy('') }
  }

  return <section className="notes-card topic-figures" aria-labelledby="figures-title">
    <p className="eyebrow">OPTIONAL · YOUR DIAGRAMS</p>
    <h2 id="figures-title">Figures in this conversation</h2>
    <p>Bring a selected figure into your normal teaching conversation when it becomes relevant. Your buddy gets its reviewed description and related notes; it does not see the picture itself.</p>
    {figures.map(figure => <FigureCard key={figure.id} figure={figure} base={base} study={study}
      setStudy={setStudy} busy={busy} setBusy={setBusy} />)}
    {!study.finished && figures.length < 3 && <details className="source-preview"><summary>Add a figure from your notes</summary>
      <p>Save a clear PNG/JPEG crop of one figure with its labels. Select its page in the uploaded PDF. You can add up to three figures before or during practice.</p>
      <form onSubmit={upload} className="upload-form">
        <label htmlFor="topic-figure-file">Figure image</label>
        <input id="topic-figure-file" type="file" accept="image/png,image/jpeg" required disabled={!!busy}
          onChange={event => { setFile(event.target.files[0] || null); retryId.current = null }} />
        <label htmlFor="topic-figure-page">Page in your PDF</label>
        <input id="topic-figure-page" type="number" min={1} max={study.document.page_count} value={page} required disabled={!!busy}
          onChange={event => { setPage(event.target.value); retryId.current = null }} />
        <label htmlFor="topic-figure-printed">Printed figure caption, if any (optional)</label>
        <input id="topic-figure-printed" value={printed} maxLength={500} disabled={!!busy}
          onChange={event => { setPrinted(event.target.value); retryId.current = null }} />
        <button className="primary compact" disabled={!file || !!busy}>Add figure with local BLIP</button>
      </form>
    </details>}
    {error && <p className="error" role="alert">{error}</p>}
  </section>
}

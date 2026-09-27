import { useRef, useState } from 'react'
import { request } from './api'

export default function DiagramPractice({ base, study, busy, setStudy }) {
  const [file, setFile] = useState(null)
  const [page, setPage] = useState(1)
  const [caption, setCaption] = useState(study.diagram?.approved_caption ?? study.diagram?.original_caption ?? '')
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')
  const retryId = useRef(null)
  const diagram = study.diagram

  async function create(event) {
    event.preventDefault()
    if (!file || working) return
    setWorking(true); setError('')
    retryId.current ||= crypto.randomUUID()
    const body = new FormData()
    body.append('file', file); body.append('page', page); body.append('request_id', retryId.current)
    try {
      const next = await request(`${base}/diagram-practices`, { method: 'POST', body })
      window.location.assign(`?session=${next.session.id}`)
    } catch (failure) { setError(failure.message) }
    finally { setWorking(false) }
  }

  async function approve() {
    setWorking(true); setError('')
    try {
      setStudy(await request(`${base}/diagram/approve`, { method: 'POST',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: caption }) }))
    } catch (failure) { setError(failure.message) }
    finally { setWorking(false) }
  }

  return <section className="notes-card diagram-card">
    <p className="eyebrow">{diagram ? 'DIAGRAM-ONLY PRACTICE' : 'OPTIONAL · EXPLAIN A DIAGRAM'}</p>
    <h2>{diagram ? 'Your diagram' : 'Explore a diagram with your buddy'}</h2>
    {error && <p className="error" role="alert">{error}</p>}
    {diagram ? <>
      <p>This conversation and reflection are separate from your topic practice. <a href={`?session=${diagram.parent_id}`}>Return to the notes session</a></p>
      <a href={`/api${base}/diagram.png`} target="_blank" rel="noreferrer" aria-label="Open diagram at full size">
        <img className="diagram-image" src={`/api${base}/diagram.png`} alt={`Selected diagram from page ${diagram.page} of your notes`} />
      </a>
      <a href={`/api${base}/notes.pdf#page=${diagram.page}`} target="_blank" rel="noreferrer">Revisit source page {diagram.page} ↗</a>
      <p>Granite generated a description of this image. Check labels, arrows and relationships against the picture. Correct anything inaccurate or say which details are unclear. This description gives the buddy context; it is not your explanation.</p>
      {!study.started ? <>
        <label htmlFor="diagram-caption">Review the diagram description</label>
        <textarea id="diagram-caption" rows={7} value={caption} maxLength={4000} disabled={working || busy}
          onChange={event => {
            setCaption(event.target.value)
            setStudy({ ...study, diagram: { ...diagram, approved_caption: null } })
          }} />
        <button className="secondary" onClick={approve} disabled={!caption.trim() || working || busy}>
          {working ? 'Saving…' : 'Save reviewed description'}</button>
        {diagram.approved_caption && <p className="notice">Description saved. You can start diagram practice below. Save again if you make further edits.</p>}
      </> : <blockquote>{diagram.approved_caption}</blockquote>}
      <details className="source-preview"><summary>Original AI description and processing time</summary>
        <p>{diagram.original_caption}</p>
        <small>{diagram.trace.model} · {diagram.trace.wall_seconds} seconds · {diagram.edited ? 'Edited during review' : 'No saved edits'}
          {diagram.trace.done_reason === 'length' ? ' · Generation reached its length limit; check for incomplete text.' : ''}</small>
      </details>
    </> : <details className="source-preview"><summary>Start a separate diagram practice</summary>
      <p>Open your PDF and save a screenshot cropped around one diagram, including its labels. Upload that PNG or JPEG and select its source page. Your topic conversation stays here; the diagram opens in its own saved session.</p>
      <form onSubmit={create} className="upload-form">
        <label htmlFor="diagram-file">Diagram image (up to 8 MB)</label>
        <input id="diagram-file" type="file" accept="image/png,image/jpeg" disabled={working || busy}
          onChange={event => { setFile(event.target.files[0] || null); retryId.current = null }} required />
        <label htmlFor="diagram-page">Page in your notes</label>
        <input id="diagram-page" type="number" min={1} max={study.document.page_count} value={page} disabled={working || busy}
          onChange={event => { setPage(event.target.value); retryId.current = null }} required />
        <button className="primary compact" disabled={!file || working || busy}>{working ? 'Granite is describing the diagram…' : 'Prepare diagram practice'}</button>
        {working && <p role="status">This one-time local image analysis may take several minutes. Keep this page open.</p>}
      </form>
    </details>}
  </section>
}

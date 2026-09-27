import { useEffect, useState } from 'react'
import { request } from './api'
import StudySession from './StudySession'

export default function App() {
  const [sessions, setSessions] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const active = sessions.find(session => session.id === activeId)

  async function loadSessions() {
    setLoading(true)
    setError('')
    try {
      const items = await request('/sessions')
      setSessions(items)
      const saved = new URLSearchParams(window.location.search).get('session')
      setActiveId(items.some(item => item.id === saved) ? saved : null)
    } catch (failure) {
      setError(failure.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
    const onBack = () => {
      setActiveId(new URLSearchParams(window.location.search).get('session'))
      setNotice('')
    }
    window.addEventListener('popstate', onBack)
    return () => window.removeEventListener('popstate', onBack)
  }, [])

  useEffect(() => {
    if (active) document.getElementById('session-heading')?.focus()
  }, [active])

  function openSession(id) {
    setActiveId(id)
    const url = new URL(window.location.href)
    if (id) url.searchParams.set('session', id)
    else url.searchParams.delete('session')
    window.history.pushState({}, '', url)
    window.scrollTo(0, 0)
    setNotice('')
  }

  async function createSession(event) {
    event.preventDefault()
    if (!name.trim() || saving) return
    setSaving(true)
    setError('')
    try {
      const session = await request('/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      setSessions(items => [session, ...items])
      openSession(session.id)
      setName('')
      setNotice('Your session is saved on this computer.')
    } catch (failure) {
      setError(failure.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Feynman Buddy home"><span className="brand-icon" aria-hidden="true">f.</span>Feynman Buddy</a>
        <span className="local-badge"><span aria-hidden="true" /> Your local study space</span>
      </header>
      <main>
        {active ? (
          <section className="session-page" aria-labelledby="session-heading">
            <button className="back-button" onClick={() => openSession(null)}>← All study sessions</button>
            <p className="eyebrow">YOUR STUDY SESSION</p>
            <h1 id="session-heading" tabIndex={-1}>{active.name}</h1>
            <p className="session-subtitle">Bring your notes, explain the ideas, and explore them with your buddy.</p>
            {notice && <p className="notice" role="status">{notice}</p>}
            <StudySession key={active.id} session={active} />
          </section>
        ) : <>
        <section className="intro">
          <p className="eyebrow">LEARN BY TEACHING</p>
          <h1>A little explaining.<br /><span>A clearer understanding.</span></h1>
          <p>Choose one topic to practise. Give it a name, bring your notes, and make space to think out loud.</p>
        </section>
        <div className="workspace">
          <aside className="session-panel" aria-label="Study sessions">
            <div className="panel-heading"><h2>Your sessions</h2><span className="count">{sessions.length}</span></div>
            <form onSubmit={createSession}>
              <label htmlFor="topic">What would you like to practise?</label>
              <input id="topic" value={name} onChange={event => setName(event.target.value)} placeholder="e.g. Gradient descent" maxLength={100} autoComplete="off" required disabled={saving || loading} />
              <button className="primary" disabled={!name.trim() || saving || loading}>{saving ? 'Saving…' : 'Create a study session'}<span aria-hidden="true">↗</span></button>
            </form>
            <div aria-live="polite" className="feedback">
              {error && <div className="error" role="alert">{error}<button className="text-button" onClick={loadSessions} disabled={loading}>Retry loading sessions</button></div>}
              {notice && <p className="notice">{notice}</p>}
            </div>
            <div className="session-list">
              {loading ? <p className="muted" role="status">Loading your sessions…</p> : sessions.length === 0 ? <p className="empty">Your first session starts with a topic.</p> : sessions.map(session => (
                <a className="session-item" key={session.id} href={`?session=${session.id}`} onClick={event => { event.preventDefault(); openSession(session.id) }}>
                  <span className="session-symbol" aria-hidden="true">✦</span><span><strong>{session.name}</strong><small>{new Date(session.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} · Saved locally</small></span><span className="arrow" aria-hidden="true">›</span>
                </a>
              ))}
            </div>
          </aside>
          <section className="study-panel" aria-labelledby="study-title">
            <div className="illustration" aria-hidden="true"><div className="paper"><span /><span /><span /></div><div className="bubble">“</div><div className="spark">✦</div></div>
            <p className="eyebrow">{active ? 'YOUR STUDY SESSION' : 'ONE TOPIC. ROOM TO EXPLORE.'}</p>
            <h2 id="study-title">{active ? active.name : 'Start with something you want to understand.'}</h2>
            <p className="study-description">{active ? 'A space for your notes, your explanations and the ideas you want to revisit.' : 'A session keeps your practice focused on the topic you choose. You can return to it whenever you are ready.'}</p>
            <ol className="steps">
              <li className={active ? 'complete' : 'current'}><span>{active ? '✓' : '1'}</span><div><strong>Name your topic</strong><small>{active ? 'Saved and ready to return to' : 'You choose what to practise'}</small></div></li>
              <li><span>2</span><div><strong>Bring your notes</strong><small>Give your buddy the material to learn from</small></div></li>
              <li><span>3</span><div><strong>Teach, explore, reflect</strong><small>Work through the ideas in your own words</small></div></li>
            </ol>
            <div className="build-note"><strong>Your local practice space</strong><p>Teach by typing or recorded speech. You can also explore a diagram in a separate practice.</p></div>
          </section>
        </div>
        </>}
      </main>
      <footer>Made for thoughtful practice.<span>Your session data is stored on this computer.</span></footer>
    </div>
  )
}

import { useEffect, useRef, useState } from 'react'
import { request } from './api'
import { createPcmRecorder } from './audio'

export default function SpeechInput({ base, disabled, onUse, onActive }) {
  const [phase, setPhase] = useState('idle')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [draft, setDraft] = useState('')
  const recorder = useRef(null)
  const stream = useRef(null)
  const timer = useRef(null)
  const mounted = useRef(true)
  const active = phase !== 'idle'
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
      clearTimeout(timer.current)
      recorder.current?.cancel()
      stream.current?.getTracks().forEach(track => track.stop())
    }
  }, [])

  async function stop() {
    clearTimeout(timer.current)
    const current = recorder.current
    if (!current) return
    recorder.current = null
    if (mounted.current) setPhase('transcribing')
    try {
      const wav = await current.stop()
      if (!mounted.current) return
      const body = new FormData(); body.append('file', wav, 'recording.wav')
      const response = await request(`${base}/transcribe`, { method: 'POST', body })
      if (mounted.current) { setResult(response); setDraft(response.text) }
    } catch (failure) { if (mounted.current) setError(failure.message) }
    finally { if (mounted.current) { setPhase('idle'); onActive(false) } }
  }

  async function start() {
    setError(''); setPhase('permission'); onActive(true)
    window.speechSynthesis?.cancel()
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode) throw new Error('Recording is unavailable in this browser. Try a current Chrome or Edge browser, or type your explanation.')
      const media = await navigator.mediaDevices.getUserMedia({ audio: true })
      if (!mounted.current) { media.getTracks().forEach(track => track.stop()); return }
      stream.current = media
      const next = await createPcmRecorder(media, stop)
      if (!mounted.current) { next.cancel(); return }
      recorder.current = next
      setPhase('recording')
      timer.current = setTimeout(stop, 60000)
    } catch (failure) {
      stream.current?.getTracks().forEach(track => track.stop())
      if (mounted.current) {
        setError(failure.name === 'NotAllowedError' ? 'Microphone access was not allowed. Allow it in your browser or type your explanation.' : failure.message)
        setPhase('idle'); onActive(false)
      }
    }
  }

  return <div className="speech-input">
    <button type="button" className="secondary" disabled={disabled || (active && phase !== 'recording')}
      onClick={phase === 'recording' ? stop : start}>{phase === 'recording' ? 'Stop recording' : 'Record explanation'}</button>
    <p className="source-context-note" role="status">{phase === 'recording' ? 'Recording… stops automatically after 60 seconds.'
      : phase === 'permission' ? 'Waiting for microphone permission…' : phase === 'transcribing' ? 'Transcribing on this computer…'
        : 'Record up to 60 seconds in English. Review the transcript before sending. Audio is not saved; transcript text stays in this local session.'}</p>
    {error && <p className="error" role="alert">{error}</p>}
    {result && <div>
      <label htmlFor="speech-review">Review and edit what was heard</label>
      <textarea id="speech-review" rows={3} value={draft} onChange={event => setDraft(event.target.value)} disabled={active || disabled} />
      {draft.length > 1200 && <p className="error">Shorten this to 1,200 characters before using it.</p>}
      <button type="button" className="secondary" disabled={active || disabled || !draft.trim() || draft.length > 1200}
        onClick={() => { onUse(draft.trim(), result.id); setResult(null); setDraft('') }}>Use transcript as explanation</button>
      <p className="source-context-note">This replaces the current explanation draft. You still choose when to send it.</p>
    </div>}
  </div>
}

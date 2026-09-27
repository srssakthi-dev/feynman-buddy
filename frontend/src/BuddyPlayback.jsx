import { useEffect, useRef, useState } from 'react'

export default function BuddyPlayback({ messages, blocked }) {
  const [voices, setVoices] = useState([])
  const [auto, setAuto] = useState(false)
  const [error, setError] = useState('')
  const latest = messages.filter(message => message.role === 'buddy').at(-1)
  const seen = useRef(latest?.id)
  const voice = voices.find(item => item.lang.startsWith('en')) || voices[0]
  useEffect(() => {
    const synth = window.speechSynthesis
    if (!synth) return
    const update = () => setVoices(synth.getVoices().filter(item => item.localService))
    update(); synth.addEventListener('voiceschanged', update)
    return () => { synth.cancel(); synth.removeEventListener('voiceschanged', update) }
  }, [])
  function speak() {
    if (!voice || !latest || blocked) return
    setError('')
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(latest.text.replace(/[*$]/g, ''))
    utterance.voice = voice
    utterance.onerror = event => { if (!['interrupted', 'canceled'].includes(event.error)) setError('Playback was unavailable. Try Listen again or read the reply.') }
    window.speechSynthesis.speak(utterance)
  }
  useEffect(() => {
    if (blocked) { window.speechSynthesis?.cancel(); return }
    if (latest?.id !== seen.current) {
      seen.current = latest?.id
      if (auto) speak()
    }
  }, [latest?.id, blocked, auto, voice])
  return <div className="buddy-playback">
    <button type="button" className="text-button" disabled={!voice || !latest || blocked} onClick={speak}>Listen to latest reply</button>
    <button type="button" className="text-button" onClick={() => window.speechSynthesis?.cancel()}>Stop voice</button>
    <label><input type="checkbox" checked={auto} disabled={!voice} onChange={event => setAuto(event.target.checked)} /> Speak new replies automatically</label>
    {!voice && <p className="source-context-note">No local playback voice is available in this browser. Text replies still work.</p>}
    {error && <p className="error" role="alert">{error}</p>}
  </div>
}

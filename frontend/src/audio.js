// Capture PCM directly: no encoded container or decodeAudioData dependency.
export function encodePcmWav(chunks, sampleRate) {
  const frames = Math.min(chunks.reduce((sum, chunk) => sum + chunk.length, 0), sampleRate * 60)
  if (frames < sampleRate * .3) throw new Error('Please record at least a moment of speech.')
  const buffer = new ArrayBuffer(44 + frames * 2)
  const view = new DataView(buffer)
  const label = (offset, text) => [...text].forEach((character, index) => view.setUint8(offset + index, character.charCodeAt(0)))
  label(0, 'RIFF'); view.setUint32(4, buffer.byteLength - 8, true); label(8, 'WAVE'); label(12, 'fmt ')
  view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true); view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true); view.setUint16(34, 16, true); label(36, 'data')
  view.setUint32(40, frames * 2, true)
  let index = 0
  for (const chunk of chunks) for (const sample of chunk) {
    if (index >= frames) break
    const clipped = Math.max(-1, Math.min(1, sample))
    view.setInt16(44 + index++ * 2, clipped < 0 ? clipped * 32768 : clipped * 32767, true)
  }
  return new Blob([buffer], { type: 'audio/wav' })
}

export async function createPcmRecorder(stream, onLimit) {
  const context = new AudioContext({ sampleRate: 16000 })
  let source, node, timeout, stopping
  const chunks = []
  const close = () => {
    clearTimeout(timeout)
    source?.disconnect(); node?.disconnect()
    stream.getTracks().forEach(track => track.stop())
    if (context.state !== 'closed') void context.close()
  }
  try {
    await context.resume()
    await context.audioWorklet.addModule('/pcm-recorder.js')
    node = new AudioWorkletNode(context, 'pcm-recorder', { processorOptions: { maxFrames: context.sampleRate * 60 } })
    source = context.createMediaStreamSource(stream)
    let finished = false
    let resolveFinish
    const finishedPromise = new Promise(resolve => { resolveFinish = resolve })
    node.port.onmessage = ({ data }) => {
      if (data.type === 'samples') chunks.push(data.samples)
      if (data.type === 'finished') {
        finished = true; resolveFinish()
        if (data.limit) onLimit()
      }
    }
    source.connect(node)
    node.connect(context.destination) // Worklet output is silence, not microphone feedback.
    return {
      stop() {
        if (!stopping) stopping = (async () => {
          try {
            if (!finished) node.port.postMessage('finish')
            await Promise.race([finishedPromise, new Promise((_, reject) => {
              timeout = setTimeout(() => reject(new Error('The microphone stopped responding. Please record again.')), 3000)
            })])
            return encodePcmWav(chunks, context.sampleRate)
          } finally { close() }
        })()
        return stopping
      },
      cancel: close,
    }
  } catch (error) { close(); throw error }
}

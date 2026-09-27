class PcmRecorder extends AudioWorkletProcessor {
  constructor(options) {
    super()
    this.pending = new Float32Array(4096)
    this.used = 0
    this.total = 0
    this.maxFrames = options.processorOptions.maxFrames
    this.finished = false
    this.port.onmessage = ({ data }) => { if (data === 'finish') this.finish(false) }
  }
  flush() {
    if (this.used) {
      const samples = this.pending.slice(0, this.used)
      this.port.postMessage({ type: 'samples', samples }, [samples.buffer])
      this.used = 0
    }
  }
  finish(limit) {
    if (this.finished) return
    this.finished = true
    this.flush()
    this.port.postMessage({ type: 'finished', limit })
  }
  process(inputs, outputs) {
    for (const output of outputs) for (const channel of output) channel.fill(0)
    if (this.finished) return true
    const channels = inputs[0]
    if (!channels?.length) return true
    for (let i = 0; i < channels[0].length; i++) {
      let sample = 0
      for (const channel of channels) sample += channel[i] / channels.length
      this.pending[this.used++] = sample
      this.total++
      if (this.used === this.pending.length) this.flush()
      if (this.total >= this.maxFrames) { this.finish(true); break }
    }
    return true
  }
}
registerProcessor('pcm-recorder', PcmRecorder)

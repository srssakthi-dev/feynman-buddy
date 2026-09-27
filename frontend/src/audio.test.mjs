import test from 'node:test'
import assert from 'node:assert/strict'
import vm from 'node:vm'
import { readFileSync } from 'node:fs'
import { encodePcmWav } from './audio.js'

function processor(maxFrames = 960000) {
  let Processor
  const outputs = []
  vm.runInNewContext(readFileSync(new URL('../public/pcm-recorder.js', import.meta.url), 'utf8'), {
    AudioWorkletProcessor: class { constructor() { this.port = { postMessage: item => outputs.push(item) } } },
    registerProcessor: (_, type) => { Processor = type }, Float32Array,
  })
  return { recorder: new Processor({ processorOptions: { maxFrames } }), outputs }
}

test('stop flushes the final partial batch before completion', () => {
  const { recorder, outputs } = processor()
  const speakers = new Float32Array(128).fill(1)
  recorder.process([[new Float32Array(128).fill(.25)]], [[speakers]])
  recorder.port.onmessage({ data: 'finish' })
  assert.equal(outputs[0].type, 'samples')
  assert.equal(outputs[0].samples.length, 128)
  assert.equal(outputs[0].samples[127], .25)
  assert.equal(outputs[1].type, 'finished')
  assert.ok(speakers.every(value => value === 0))
  recorder.port.onmessage({ data: 'finish' })
  assert.equal(outputs.length, 2)
})

test('recording limit caps samples and stereo input becomes mono', () => {
  const { recorder, outputs } = processor(50)
  recorder.process([[new Float32Array(128).fill(.8), new Float32Array(128).fill(.2)]], [])
  assert.equal(outputs[0].samples.length, 50)
  assert.equal(outputs[0].samples[0], .5)
  assert.equal(outputs[1].limit, true)
})

test('captured samples produce complete 16-bit PCM WAV with clipped samples', async () => {
  const samples = new Float32Array(8000).fill(.25)
  samples[0] = -2; samples[7999] = 2
  const wav = encodePcmWav([samples.slice(0, 4000), samples.slice(4000)], 16000)
  const data = new DataView(await wav.arrayBuffer())
  assert.equal(wav.size, 16044)
  assert.equal(data.getUint32(24, true), 16000)
  assert.equal(data.getUint16(22, true), 1)
  assert.equal(data.getUint32(40, true), 16000)
  assert.equal(data.getInt16(44, true), -32768)
  assert.equal(data.getInt16(16042, true), 32767)
})

test('empty or very short capture reports an actionable error', () => {
  assert.throws(() => encodePcmWav([], 16000), /record at least/)
})

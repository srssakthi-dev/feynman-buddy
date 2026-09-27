# Speech integration checkpoint

## Recording correction, 28 September 2026
The user's first microphone trial failed with "Unable to decode audio data" in the browser conversion stage, before transcription. The previous MediaRecorder -> decodeAudioData route depended on browser support for decoding the recorded compressed container. The precise codec/container failure was not reproduced from a saved recording, so it is not claimed as a confirmed codec diagnosis.

The current implementation replaces that conversion route with direct AudioWorklet PCM capture and WAV encoding. It no longer calls MediaRecorder or decodeAudioData. Stop requests flush the final partial sample batch before the microphone/context are released. The worklet emits silence to the output to avoid microphone feedback and limits captured samples to 60 seconds. Transcript review and the backend route remain unchanged.

Four new Node regression tests pass: final sample flush/order, sample cap and stereo downmix, PCM WAV headers/sample encoding, and rejection of insufficient capture. A one-second synthetic waveform encoded by the actual frontend encoder was accepted by the actual backend WAV decoder (16000 samples). Frontend build and lint pass. These checks validate the codec-independent data path, not a successful live microphone trial; retrying in the user's browser remains necessary.

For the Chapter 4.8 draft below, replace its description of browser decoding with: "The browser captures microphone samples directly through an AudioWorklet and encodes them as mono PCM WAV. This avoids decoding a compressed recording before transcription." The earlier implementation and failed fixture results below are historical evidence, not the current capture mechanism.

## Implemented behaviour
An unfinished practice now offers Record explanation and Stop recording. The browser requests microphone permission and records up to 60 seconds. It stops playback before recording. Browser audio decoding and an OfflineAudioContext convert the captured clip to mono 16 kHz, 16-bit PCM WAV before upload; no FFmpeg binary is required by this path.

The session-scoped transcription endpoint validates WAV format, duration, size and basic signal level, then passes a NumPy waveform to the locally cached Whisper base model on CPU. English and transcription mode are explicit; FP16 is disabled. A missing local checkpoint produces an error rather than initiating a download. A quiet-signal check is not a speech detector: noise and hallucinated ASR output remain possible.

Transcription does not append a conversation message. The UI first shows an editable transcript. Use transcript as explanation explicitly replaces the explanation draft; Send explanation submits the reviewed text through the existing retrieval and dialogue path. Original recognition text, duration and processing time are stored locally. A sent turn links the original transcript to its student message and records whether it changed. The raw recording is processed in memory and is not saved by the backend; unsubmitted transcript text remains in the local database.

Buddy playback offers Listen to latest reply, Stop voice and optional automatic playback for new replies. Only browser voices marked localService are eligible. If none exists, the interface states that playback is unavailable and preserves text use. Speech is cancelled before recording and on component unmount. This uses a browser/OS service rather than a separately evaluated pretrained model and is not counted as an additional model for the template.

## Code map
- frontend/src/SpeechInput.jsx: recording lifecycle, microphone errors and editable review.
- frontend/src/audio.js: browser decoding, resampling and WAV encoding.
- frontend/src/BuddyPlayback.jsx: local voice selection, replay/stop and optional new-reply playback.
- backend/app/services/speech.py: WAV validation, waveform conversion and local Whisper inference.
- backend/app/study_routes.py: session-scoped transcription and association with reviewed turns.
- backend/app/storage.py: additive schema version 3, transcription text and metadata.
- backend/tests/test_speech.py: audio and API workflow tests.

## Verification and its limits
33 backend tests passed after this change; eight are new audio/service/workflow tests. They verify mono resampling, malformed/truncated/quiet/overlong audio rejection, missing-checkpoint handling, CPU inference arguments, explicit review before sending, original-vs-edited transcript provenance and cross-session isolation. Model responses are mocked in these tests. Frontend build and lint pass.

The real Whisper base checkpoint loaded successfully on CPU in 0.932 seconds in a separate process. This is a model-load check, not a transcription-quality result. A synthetic speech fixture attempt using Windows System.Speech stalled and left an empty file. The endpoint correctly rejected that incomplete file with HTTP 422. The attempt and result are preserved in evaluation/results/speech_smoke_fixture_incomplete.json. Both helper processes were stopped; no user application server was stopped. No successful real spoken-audio transcription or audible browser-playback trial was completed in this checkpoint. Do not report a word-error rate, end-to-end success rate or human speech accuracy from these checks.

The new browser controls have passed build/lint, not a full microphone-permission or audible playback browser trial. The user's microphone/browser check is the remaining integration verification. System responsiveness still includes the existing LLM generation delay; adding speech has not made it real-time.

## Manual trial
1. Restart the backend, refresh the frontend and create/start an unfinished practice with notes.
2. Choose Record explanation, allow microphone access and speak one short explanation. Stop recording.
3. Compare the transcript with what was said. Edit any error and choose Use transcript as explanation. Confirm that no buddy reply occurs until Send explanation is selected.
4. Send and inspect the resulting conversation. Download evidence to verify the original transcript, edit flag and timing attached to the turn.
5. Choose Listen to latest reply, then Stop voice. If a local voice is available, try optional automatic playback. Confirm that starting a recording stops playback.
6. Check microphone denial, a quiet recording, navigating away during recording, and restoration of ordinary typed input after an error. Record actual outcomes rather than assuming success.

For later ASR evaluation, record a small consented set of real clips with reference transcripts, including mathematical vocabulary and ordinary room noise. Compare recognised and reference words, correction burden and transcription time. The current base choice reuses the installed model; it has not won a controlled ASR candidate comparison.

## Chapter 4 draft: 4.8 Speech Interaction
The speech input pathway allows the learner to record an explanation and review its transcription before submitting it. The browser captures audio, decodes the recording and converts it into mono 16 kHz PCM WAV. The backend validates the recording and supplies the waveform to a locally cached Whisper base model running on CPU. This avoids requiring an external transcription API or an FFmpeg subprocess in the application's recording path.

Recognition and submission are separate actions. The returned transcript appears in an editable field, allowing the learner to correct technical terms or recognition errors. Only the reviewed text enters the existing retrieval and conversational generation workflow. The database retains the original transcript and records whether the submitted text was edited, supporting later analysis of recognition errors and correction effort. Raw audio is not retained by the backend.

The interface also includes replay and stop controls for buddy responses, with optional playback of new replies. Playback selects only voices identified by the browser as local and stops when microphone recording begins. Text interaction remains available if microphone permission or local playback is unavailable. These controls implement a turn-based speech workflow; they do not remove the measured language-model delay or establish real-time performance. Microphone accuracy and audible playback still require an end-to-end user trial.

## Technical references
- OpenAI Whisper implementation: https://github.com/openai/whisper/blob/main/whisper/transcribe.py
- Browser recording: https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API
- Local voice flag: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/localService

## Next scope boundary
Diagram extraction, caption review and retrieval integration remain unimplemented. The complete chosen audio/image/text workflow is therefore not yet ready for the final integrated demonstration.

## User verification, 28 September 2026
The student reported that the audio fix worked after testing. This confirms a user-observed successful integration trial; no transcript/reference pair or WER score was collected.

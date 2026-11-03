# Lab 2 verification record

**Last reviewed:** November 3, 2026. This file separates actual execution evidence from unverified capabilities.

| Check | Status | Evidence |
| --- | --- | --- |
| FastAPI route and validation unit tests | PASS | [Contract test workflow](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-api-tests.yml); classifier is deliberately mocked |
| Actual Hugging Face ONNX model loaded and executed | PASS | [Real model and HTTP workflow](https://github.com/hpban2527-ui/assignment-1/actions/runs/41642386647) |
| Live requests-based HTTP API against Uvicorn | PASS | Same workflow, independent checks of GET /, GET /health and POST /predict |
| Two predictions shown in actual Swagger execution | PASS | [Recorded desktop and actual browser network responses](https://github.com/hpban2527-ui/assignment-1/actions/runs/41643375258) |
| Invalid blank input returned HTTP 422 | PASS | Same real-screen workflow |
| Real 1600×900 screencast with captions/audio | PASS | [Final personal-voice video release](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-personal-voice-25127009); original recording archived |
| GitHub public source on main | PASS | [Source folder](https://github.com/hpban2527-ui/assignment-1/tree/main/lab2-sentiment-fastapi) |
| Public Vercel GET / and GET /health | VERIFIED | Public endpoints were fetched externally |
| Public Vercel POST /predict real inference | NOT VERIFIED | Do not infer this from a READY deployment or CI run |
| Personalized narration synthesized from the speaker-authorized recording | PASS — 15 segments, timing and text checked | [Final 3m40s MP4](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-personal-voice-25127009), [QA report](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-personal-voice-25127009/voice_video_qa.json) — F5-TTS v1, **not** HeyGen voice clone |
| Independent perceptual verification of speaker identity/voice resemblance | NOT CERTIFIED | ASR text similarity is not an identity similarity metric; speaker must judge naturalness personally |
| Original video stream preserved exactly after new narration | PASS | SHA-256 of H.264 stream identical before/after replacement; see QA report |
| Raw authorized voice reference in public repository | NONE | Reference audio and intermediate voice WAV files were kept out of the public repository |

Measured ONNX int8 outputs from the real model:
- `I really love this movie!` -> POSITIVE, **0.9998676776885986**
- `This was a terrible experience.` -> NEGATIVE, **0.9992380142211914**

**Privacy:** Do not publish voice reference clips, private test credentials, or personal tokens to GitHub. All required public links point to source, workflows, or the final demonstrated video.

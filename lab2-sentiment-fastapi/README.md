# Lab 2 — Hugging Face Sentiment Analysis API

[![FastAPI contract tests](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-api-tests.yml/badge.svg)](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-api-tests.yml)
[![Real Hugging Face inference](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-real-integration.yml/badge.svg)](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-real-integration.yml)

**Computational Thinking · HCMUS · Student: Huỳnh Phương Bình An · ID: 25127009 · Class: 25C09**

A small, fully documented FastAPI service that uses **real pre-trained Hugging Face model weights** to classify English text as positive or negative. Inference uses a CPU-friendly ONNX int8 model; no GPU or model training is required.

**Quick links:** [Final submission demo MP4 — student introduction, 3m 55s](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-final-25127009/LAB2_FINAL_25127009.mp4) · [Release page](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-actual-screen-25127009) · [Source](main.py) · [Public Swagger UI](https://hcmus-lab2-sentiment-25127009.vercel.app/docs) · [Measured model + HTTP test](https://github.com/hpban2527-ui/assignment-1/actions/runs/41642386647)

## Model

- Checkpoint: [Xenova/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english), file `onnx/model_int8.onnx`.
- Original fine-tuned model: [distilbert/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english).
- Task: binary English sentiment analysis. The model does **not** classify neutral sentiment, detect sarcasm reliably, or support every language.

## Run locally

Python 3.11 or 3.12 is recommended. From this directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs**. The first real prediction downloads the model and tokenizer from Hugging Face into the local model cache. An Internet connection is needed for the first download.

## API specification

| Route | Description | Success |
| --- | --- | --- |
| `GET /` | Short introduction and model information | HTTP 200, JSON |
| `GET /health` | API availability and whether the model has been loaded in this process | HTTP 200, JSON |
| `POST /predict` | Validate user text, invoke the Hugging Face model, return classification and score | HTTP 200, JSON |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"I really love this movie!"}'
```

**Actually measured** responses from successful real-model execution in GitHub Actions on November 3, 2026 (not mock outputs):

```json
{"label":"POSITIVE","score":0.9998676776885986,"model":"Xenova/distilbert-base-uncased-finetuned-sst-2-english"}
```

```json
{"label":"NEGATIVE","score":0.9992380142211914,"model":"Xenova/distilbert-base-uncased-finetuned-sst-2-english"}
```

The second response used `{"text":"This was a terrible experience."}`.

A missing, whitespace-only, incorrectly typed, or overlength `text` field gives **HTTP 422**. A model download or inference failure gives **HTTP 503** with a safe error message. Inputs are limited to 2,000 characters and tokenized text is truncated to the model's 512-token limit.

## Tests and reproducibility

```bash
# Lightweight API contract tests: model replaced by a test double
python -m pytest -q

# Separate acceptance test: actual downloaded ONNX model (NO mock)
python check_real_model.py

# Against a running Uvicorn server — real HTTP via requests
python test_api.py --base-url http://127.0.0.1:8000
```

The two testing categories are intentionally distinct. The offline unit tests **do not prove model inference**. Real model execution and live HTTP integration were independently recorded and passed in [this GitHub Actions run](https://github.com/hpban2527-ui/assignment-1/actions/runs/41642386647); the [real-model integration workflow](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-real-integration.yml) is also reproducible.

### Source layout

```text
main.py                    FastAPI routes, validation and ONNX inference
check_real_model.py        Direct REAL Hugging Face model acceptance
test_api.py                Live HTTP API checks using requests
tests/test_main.py         Offline API contract tests (mock classifier)
requirements.txt           Python dependencies
requirements-ci.txt        Lightweight test dependencies
scripts/                   Reproducible real-screen recording and editing tools
README.md                  Usage, sample requests, real results, demo link
VERIFICATION.md            Evidence and remaining limitations
```

A Jupyter notebook is not included because Colab/Jupyter were **not used** to develop this project.

## Final submission video — real screen recording

**[Watch/download the final Lab 2 MP4 (3 minutes 55 seconds)](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-final-25127009/LAB2_FINAL_25127009.mp4)**

**Student:** Huỳnh Phương Bình An · **Student ID:** 25127009 · **Class:** 25C09.

The video begins with a **15.2-second academic introduction** displaying the student's full name with correct Vietnamese diacritics, ID, and class, accompanied by a concise English voice-conditioned introduction. The background preview is taken from the **real Swagger recording**, not generated or fabricated.

The subsequent **220 seconds** are the independently recorded screen demonstration: GitHub source, Hugging Face model page, terminal commands, genuine ONNX inference, Uvicorn, Swagger **Try it out → Execute** for `GET /`, `GET /health`, two `POST /predict` predictions, HTTP 422 validation, and the Python `requests` test.

**Video integrity:** The original demonstration contains **3,300 frames**. All **3,300/3,300 frames** were independently compared after adding the introduction and confirmed **pixel-identical**. Final output: 1600 × 900, 15 fps, H.264/AAC, **235.221 seconds**, under the five-minute limit.

**Narration:** The English audio is *synthesized with F5-TTS using the speaker's expressly authorized reference recording*; it is not a live microphone recording and not a paid HeyGen clone. The level of subjective resemblance has not been independently certified. No personal reference audio or intermediate generated WAVs were committed to GitHub.

[Final video release and download](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-final-25127009) · [Final QA report](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-final-25127009/final_video_qa.json) · [Release and file integrity workflow — PASS](https://github.com/hpban2527-ui/assignment-1/actions/runs/41671234923) · [Original screen-recording verification](https://github.com/hpban2527-ui/assignment-1/actions/runs/41643375258)

The [220-second personal-voice recording without the student introduction](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-personal-voice-25127009) remains archived for comparison.

**Submission:** Provide a plain UTF-8 file named `25127009.txt` containing only the repository URL `https://github.com/hpban2527-ui/assignment-1`, as required by the lab's submission format.

## Public deployment status

The FastAPI project is deployed at [Vercel](https://hcmus-lab2-sentiment-25127009.vercel.app/). Public `GET /` and `GET /health` were verified. The full prediction pipeline was **separately** verified end-to-end on GitHub Actions; `POST /predict` on the Vercel deployment has **not** been independently accepted, so no claim is made that the hosted server completes model inference.

**Integrity note:** This project was developed with AI assistance for code preparation, testing and demo production. The reported inference scores, API responses and passing workflows are measured evidence, not fabricated examples. No private voice reference recordings belong in this public repository.

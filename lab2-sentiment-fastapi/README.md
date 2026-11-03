# Lab 2 — Hugging Face Sentiment Analysis API

[![FastAPI contract tests](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-api-tests.yml/badge.svg)](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-api-tests.yml)
[![Real Hugging Face inference](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-real-integration.yml/badge.svg)](https://github.com/hpban2527-ui/assignment-1/actions/workflows/lab2-real-integration.yml)

**Computational Thinking · HCMUS · Student: Huỳnh Phương Bình An · ID: 25127009 · Class: 25C09**

A small, fully documented FastAPI service that uses **real pre-trained Hugging Face model weights** to classify English text as positive or negative. Inference uses a CPU-friendly ONNX int8 model; no GPU or model training is required.

**Quick links:** [Demo MP4 (3m 40s)](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-actual-screen-25127009/LAB2_REAL_SCREEN_DEMO_25127009.mp4) · [Release page](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-actual-screen-25127009) · [Source](main.py) · [Public Swagger UI](https://hcmus-lab2-sentiment-25127009.vercel.app/docs) · [Measured model + HTTP test](https://github.com/hpban2527-ui/assignment-1/actions/runs/41642386647)

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

## Demonstration video — actual screen recording

[**Watch/download the final screen-recorded MP4 (3m 40s)**](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-actual-screen-25127009/LAB2_REAL_SCREEN_DEMO_25127009.mp4)

The video records a visible Linux desktop with Chrome and xterm: model page, public GitHub source, Python dependencies and commands, real ONNX inference, Uvicorn startup, Swagger **Try it out → Execute** on all three endpoints, two genuine sentiment predictions, HTTP 422 invalid input, and `requests` integration tests. It has English narration and captions. The video was produced with an AI-generated narration voice; it is **not represented as the student's original speech or verified personal voice clone**. The on-screen HTTP responses are grounded in the recorded network requests.

[Screen recording acceptance log](https://github.com/hpban2527-ui/assignment-1/actions/runs/41643375258) · [MP4 release](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-actual-screen-25127009)

## Public deployment status

The FastAPI project is deployed at [Vercel](https://hcmus-lab2-sentiment-25127009.vercel.app/). Public `GET /` and `GET /health` were verified. The full prediction pipeline was **separately** verified end-to-end on GitHub Actions; `POST /predict` on the Vercel deployment has **not** been independently accepted, so no claim is made that the hosted server completes model inference.

**Integrity note:** This project was developed with AI assistance for code preparation, testing and demo production. The reported inference scores, API responses and passing workflows are measured evidence, not fabricated examples. No private voice reference recordings belong in this public repository.

# Computational Thinking — Lab 2: English Sentiment Analysis API

**Student:** Huỳnh Phương Bình An · **ID:** 25127009 · **Class:** 25C09

This FastAPI application exposes a **real Hugging Face pre-trained DistilBERT SST-2 sentiment classifier** for English text. It uses an int8 ONNX checkpoint (CPU, no GPU required) instead of large PyTorch weights.

## Hugging Face model

- Used checkpoint: [Xenova/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english), `onnx/model_int8.onnx`
- Original fine-tuned checkpoint: [distilbert/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
- Task: English text classification, positive/negative sentiment.
- Python packages: FastAPI, uvicorn, onnxruntime, huggingface-hub, tokenizers, numpy.

## Project source

`main.py`: API endpoints, Pydantic input validation, caching and inference.
`test_api.py`: HTTP verification with requests (two model predictions).
`check_real_model.py`: run **real** Hugging Face checkpoint to verify it was downloaded and produces correct predictions; no mocks.
`tests/test_main.py`: mocked offline contract tests, distinct from real inference.
`requirements.txt`: dependencies.
`README.md`: documentation and examples.

## Install and run

Python 3.11/3.12 recommended:

```bash
python -m venv .venv
# On Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs for interactive Swagger requests. The first prediction downloads ~67MB real ONNX model weights and its tokenizer from Hugging Face.

## Required API

| Endpoint | Purpose |
|---|---|
| `GET /` | Introduction, model description and docs link |
| `GET /health` | Service health, `model_loaded` state |
| `POST /predict` | Real model inference, returns JSON label, score, model |

```json
POST /predict
{"text": "I really love this movie!"}
```

Response format (confidence score below is **illustrative**, not measured):

```json
{"label":"POSITIVE","score":0.99,"model":"Xenova/distilbert-base-uncased-finetuned-sst-2-english"}
```

Second input: `{"text":"This was a terrible experience."}` → NEGATIVE.

Pydantic rejects missing/empty/whitespace-only text, wrong type, or text longer than 2000 characters (HTTP 422); failed model download/inference returns safe HTTP 503.

## Testing (mock vs real)

```bash
python -m pytest -q
python check_real_model.py
# In another terminal while uvicorn is running:
python test_api.py --base-url http://127.0.0.1:8000
```

- Offline contract suite uses a mocked classifier, so this alone does **not** prove real-model inference.
- `check_real_model.py` loads and executes ONNX model weights from Hugging Face; build fails if predictions disagree with expected labels.
- `test_api.py` calls actual HTTP server via requests with two contrasting inputs, plus invalid input cases.

## Video demonstration (max 5 minutes)

**Actual screen-recorded demo (3 minutes 40 seconds):** [Watch or download the verified MP4 video](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-actual-screen-25127009/LAB2_REAL_SCREEN_DEMO_25127009.mp4).

**Public video release page:** https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-actual-screen-25127009

This is a real 1600 × 900 on-screen recording (not a slideshow), showing the Hugging Face model page, public source, terminal commands, real ONNX inference, running Uvicorn, Swagger **Try it out → Execute** for `GET /`, `GET /health`, two `POST /predict` examples (positive and negative), HTTP 422 validation, and the Python `requests` test. It has English female narration and synchronized captions. All five Swagger HTTP responses were verified against actual Chrome network requests. [Read the independent screen-recording workflow logs](https://github.com/hpban2527-ui/assignment-1/actions/runs/41643375258).

## Deployment

Render Free Python service:
- Repo: `https://github.com/hpban2527-ui/assignment-1`
- Branch: `lab2/fastapi-huggingface-20261103` (until merge to main)
- Build command: `cd lab2-sentiment-fastapi && pip install -r requirements.txt && python check_real_model.py`
- Start command: `cd lab2-sentiment-fastapi && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health path: `/health`

The public deployment must be verified before any claim of real-model runtime acceptance. ONNX int8 scores can differ slightly from full-float PyTorch. English-only binary classifier, limited on sarcasm/nuance.

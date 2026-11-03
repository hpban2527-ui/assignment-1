# Lab 2 — Sentiment Analysis API

**Student:** Huỳnh Phương Bình An  
**Student ID:** 25127009  
**Class:** 25C09  
**Course:** Computational Thinking

## Overview

This project provides an English sentiment analysis REST API built with **FastAPI** and a pretrained **DistilBERT** model from Hugging Face. It classifies an input sentence as `POSITIVE` or `NEGATIVE` and returns a confidence score.

**Model:** [Xenova/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english)  
**Inference:** Quantized ONNX model, CPU.

## Project structure

```text
.
├── main.py
├── test_api.py
├── check_real_model.py
├── requirements.txt
├── requirements-ci.txt
├── tests/
│   └── test_main.py
└── README.md
```

## Installation and running

Python 3.11 or 3.12 is recommended. Run the following commands in the repository root:

```bash
python -m venv .venv
```

Activate the environment:

- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Install the dependencies and start FastAPI:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** for interactive API documentation. The first prediction downloads the model from Hugging Face.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | API information |
| GET | `/health` | Server status |
| POST | `/predict` | Predict English text sentiment |

### Request

```json
{
  "text": "I really love this movie!"
}
```

### Example response

```json
{
  "label": "POSITIVE",
  "score": 0.9998676776885986,
  "model": "Xenova/distilbert-base-uncased-finetuned-sst-2-english"
}
```

The sentence `This was a terrible experience.` produces `NEGATIVE`. Missing, blank, or incorrectly formatted input returns HTTP 422.

## Testing

Unit tests:

```bash
python -m pytest -q
```

Check real Hugging Face inference:

```bash
python check_real_model.py
```

With Uvicorn running in another terminal, test the HTTP endpoints:

```bash
python test_api.py --base-url http://127.0.0.1:8000
```

## Video demonstration

[**Lab 2 — Final video (MP4)**](https://github.com/hpban2527-ui/lab2-fastapi-huggingface/releases/download/lab2-final-25127009/LAB2_FINAL_25127009.mp4)

The video introduces the project, shows the Python source, runs the Hugging Face model, and demonstrates the FastAPI endpoints and example responses.


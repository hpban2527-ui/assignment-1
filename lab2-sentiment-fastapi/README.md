# Lab 2 — Sentiment Analysis API

**Student:** Huỳnh Phương Bình An  
**Student ID:** 25127009  
**Class:** 25C09  
**Course:** Computational Thinking

## Overview

This project implements a REST API for English sentiment analysis using **FastAPI** and a pretrained **DistilBERT** model from Hugging Face. The API accepts a sentence and returns its predicted sentiment (`POSITIVE` or `NEGATIVE`) with a confidence score.

**Model:** [Xenova/distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english)

## Project files

| File | Description |
| --- | --- |
| `main.py` | FastAPI application and model inference |
| `test_api.py` | HTTP tests using `requests` |
| `check_real_model.py` | Model inference test |
| `tests/test_main.py` | API unit tests |
| `requirements.txt` | Python dependencies |

## Installation

Python 3.11 or 3.12 is recommended. Open a terminal in the `lab2-sentiment-fastapi` directory.

```bash
python -m venv .venv
```

Activate the environment:

- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Install the dependencies and start the server:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** to test the API through Swagger UI. The model files are downloaded automatically on the first prediction.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | API information |
| GET | `/health` | Server health check |
| POST | `/predict` | Predict text sentiment |

### Example request

```http
POST /predict
Content-Type: application/json

{"text": "I really love this movie!"}
```

### Example response

```json
{
  "label": "POSITIVE",
  "score": 0.9998676776885986,
  "model": "Xenova/distilbert-base-uncased-finetuned-sst-2-english"
}
```

A second example, `"This was a terrible experience."`, returns the label `NEGATIVE`. Invalid input returns HTTP 422.

## Testing

Run the unit tests:

```bash
python -m pytest -q
```

Test the Hugging Face model:

```bash
python check_real_model.py
```

With the FastAPI server running, test the endpoints:

```bash
python test_api.py --base-url http://127.0.0.1:8000
```

## Demo video

[**Lab 2 — Video demonstration (MP4)**](https://github.com/hpban2527-ui/assignment-1/releases/download/lab2-final-25127009/LAB2_FINAL_25127009.mp4)

The video introduces the project and demonstrates the source code, model execution, API endpoints, sample predictions, and input validation.

## Submission

Repository: https://github.com/hpban2527-ui/assignment-1


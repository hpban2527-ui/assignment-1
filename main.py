"""Hugging Face DistilBERT sentiment inference through quantized ONNX on CPU."""

import logging
import os
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

MODEL_ID = "Xenova/distilbert-base-uncased-finetuned-sst-2-english"
MODEL_FILE = "onnx/model_int8.onnx"
logger = logging.getLogger(__name__)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

app = FastAPI(
    title="English Sentiment Analysis API",
    description="Classify English text as POSITIVE or NEGATIVE using a real Hugging Face DistilBERT model.",
    version="1.1.0",
)


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000, description="English text (1–2000 characters)")

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text must not be empty or whitespace only")
        return value


class PredictResponse(BaseModel):
    label: Literal["POSITIVE", "NEGATIVE"]
    score: float = Field(ge=0.0, le=1.0)
    model: str


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Load Hugging Face tokenizer and REAL quantized ONNX model once per process."""
    import numpy as np
    import onnxruntime as ort
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer

    tokenizer_path = hf_hub_download(repo_id=MODEL_ID, filename="tokenizer.json")
    model_path = hf_hub_download(repo_id=MODEL_ID, filename=MODEL_FILE)
    tokenizer = Tokenizer.from_file(tokenizer_path)
    tokenizer.enable_truncation(max_length=512)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(model_path, sess_options=options, providers=["CPUExecutionProvider"])
    inputs = {input_.name for input_ in session.get_inputs()}
    if "input_ids" not in inputs or "attention_mask" not in inputs:
        raise RuntimeError(f"Unexpected ONNX inputs: {sorted(inputs)}")

    def classify(text: str, **_kwargs):
        encoded = tokenizer.encode(text)
        feed = {
            "input_ids": np.asarray([encoded.ids], dtype=np.int64),
            "attention_mask": np.asarray([encoded.attention_mask], dtype=np.int64),
        }
        if "token_type_ids" in inputs:
            feed["token_type_ids"] = np.asarray([encoded.type_ids], dtype=np.int64)
        logits = session.run(None, feed)[0][0]
        exp = np.exp(logits - np.max(logits))
        scores = exp / exp.sum()
        index = int(np.argmax(scores))
        labels = ("NEGATIVE", "POSITIVE")
        return [{"label": labels[index], "score": float(scores[index])}]

    logger.info("Loaded real Hugging Face model %s (%s)", MODEL_ID, MODEL_FILE)
    return classify


@app.get("/", tags=["System"])
def root():
    return {
        "message": "English Sentiment Analysis API",
        "description": "Send English text to POST /predict for POSITIVE/NEGATIVE classification.",
        "model": MODEL_ID,
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "model_loaded": get_sentiment_pipeline.cache_info().currsize > 0}


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict(request: PredictRequest):
    try:
        result = get_sentiment_pipeline()(request.text)[0]
        return PredictResponse(label=result["label"], score=float(result["score"]), model=MODEL_ID)
    except Exception as exc:
        logger.exception("Sentiment prediction failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="Sentiment model unavailable. Check model download and logs.") from exc

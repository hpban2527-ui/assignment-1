"""Acceptance test: execute actual Hugging Face ONNX weights, no mocks."""

from main import MODEL_ID, MODEL_FILE, get_sentiment_pipeline


def main():
    model = get_sentiment_pipeline()
    cases = (
        ("I really love this movie!", "POSITIVE"),
        ("This was a terrible experience.", "NEGATIVE"),
    )
    for sample, expected in cases:
        result = model(sample)[0]
        print(f"REAL_MODEL_RESULT {sample!r} => {result}", flush=True)
        assert result["label"] == expected, (expected, result)
        assert 0 < float(result["score"]) <= 1
    print(f"REAL_MODEL_VERIFIED {MODEL_ID} {MODEL_FILE}", flush=True)


if __name__ == "__main__":
    main()

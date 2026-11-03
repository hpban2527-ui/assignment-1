"""Run against a live server: python test_api.py --base-url http://127.0.0.1:8000"""

import argparse
import sys

import requests


def check_json_response(response, expected_status=200):
    if response.status_code != expected_status:
        raise AssertionError(f"HTTP {response.status_code}: {response.text}")
    result = response.json()
    if not isinstance(result, dict):
        raise AssertionError(f"Expected JSON object: {result}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Test the live sentiment API with requests.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    try:
        root = check_json_response(requests.get(base_url + "/", timeout=10))
        assert "message" in root
        print("PASS GET /")

        health = check_json_response(requests.get(base_url + "/health", timeout=10))
        assert health["status"] == "ok"
        print("PASS GET /health")

        examples = [
            ("I really love this movie!", "POSITIVE"),
            ("This was a terrible experience.", "NEGATIVE"),
        ]
        for sample, expected_label in examples:
            response = requests.post(base_url + "/predict", json={"text": sample}, timeout=args.timeout)
            result = check_json_response(response)
            assert result["label"] == expected_label, result
            assert 0 <= result["score"] <= 1, result
            assert isinstance(result["model"], str) and result["model"], result
            print(f"PASS POST /predict: {sample!r} -> {result}")

        invalid = requests.post(base_url + "/predict", json={"text": "   "}, timeout=10)
        check_json_response(invalid, expected_status=422)
        print("PASS validation: whitespace-only input returns 422")

        missing = requests.post(base_url + "/predict", json={}, timeout=10)
        check_json_response(missing, expected_status=422)
        print("PASS validation: missing text returns 422")
        print("ALL LIVE API TESTS PASSED")
        return 0
    except (requests.RequestException, AssertionError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Lab 2 demo script — maximum 5 minutes

This is a script, **not** a real recorded demo or real inference proof.

00:00–00:30: introduce course assignment and show the Hugging Face ONNX DistilBERT SST-2 model page.

00:30–01:10: show main.py, requirements.txt, test_api.py and explain endpoints and validation.

01:10–01:40: show real running FastAPI terminal and Swagger /docs.

01:40–02:10: test GET / and GET /health; explain HTTP status.

02:10–03:00: call POST /predict with `I really love this movie!`; show **actual response** and explain positive label and confidence.

03:00–03:50: call POST /predict with `This was a terrible experience.`; show **actual response** and explain negative prediction.

03:50–04:15: try whitespace-only text and show HTTP 422.

04:15–04:45: run python test_api.py against real server and show its actual result.

Never claim mocked offline output is real HF inference. Use actual video capture and upload the recording link into README.md.

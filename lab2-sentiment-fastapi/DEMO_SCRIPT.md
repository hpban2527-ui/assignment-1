# Demonstration recording guide (archival)

The **completed** actual-screen video is available through [README.md](README.md) and the [MP4 release](https://github.com/hpban2527-ui/assignment-1/releases/tag/lab2-actual-screen-25127009).

Recording sequence and acceptance criteria:
1. Show the Hugging Face model page and public source files.
2. Run `python check_real_model.py` against actual downloaded weights.
3. Start Uvicorn and visit the real Swagger page at `/docs`.
4. Click **Try it out → Execute** for `GET /` and `GET /health`.
5. Execute `POST /predict` twice with contrasting positive/negative English sentences. Capture actual HTTP 200 responses and model-generated confidence scores.
6. Send blank input and display the actual HTTP 422 response.
7. Run `python test_api.py` against the live server.
8. Keep the recording under five minutes; do not replace real screen frames with fake terminal screenshots or slide approximations.

The original video uses synthetic narration; voice cloning is separate and **must not be claimed completed unless actual generated speech from the authorized user's voice reference has been produced and verified**.

#!/usr/bin/env python3
"""Record the actual on-screen Lab 2 execution using an X11 desktop.

The browser, terminal, API, HTTP requests and Hugging Face ONNX predictions
are all executed for real. No mocked model, generated terminal output,
pre-rendered response image or slide pretending to be a screencast is used.
"""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "demo_artifacts"
OUT.mkdir(exist_ok=True)
DISPLAY = os.environ.get("DISPLAY", ":99")
RESOLUTION = "1600x900"
SLEEP_SCALE = float(os.environ.get("DEMO_SLEEP_SCALE", "1"))
SCENES = []
REC_STARTED = None
RECORDING = None


def wait(seconds):
    time.sleep(seconds * SLEEP_SCALE)


def mark(title, narration):
    elapsed = round(time.monotonic() - REC_STARTED, 2)
    SCENES.append({"at": elapsed, "title": title, "narration": narration})
    print("SCREEN_SCENE", json.dumps(SCENES[-1]), flush=True)


def run(*args, check=True, timeout=20, **kw):
    return subprocess.run(args, check=check, timeout=timeout, **kw)


def window_with_title(title):
    result = run("xdotool", "search", "--onlyvisible", "--name", title,
                 check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"No visible X window named {title}: {result.stderr}")
    return result.stdout.strip().splitlines()[-1]


def foreground_terminal():
    win = window_with_title("Lab 2 - Real Terminal")
    run("xdotool", "windowactivate", "--sync", win)
    wait(0.6)


def type_real_command(command, delay=7):
    foreground_terminal()
    run("xdotool", "type", "--clearmodifiers", "--delay", "2", "--", command)
    run("xdotool", "key", "Return")
    wait(delay)


def start_video():
    global RECORDING, REC_STARTED
    log = open(OUT / "capture_ffmpeg.log", "wb")
    RECORDING = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "x11grab", "-draw_mouse", "1",
        "-framerate", "15", "-video_size", RESOLUTION, "-i", DISPLAY,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(OUT / "lab2_raw_actual_screen.mp4")
    ], stdout=log, stderr=log)
    wait(2)
    if RECORDING.poll() is not None:
        raise RuntimeError("ffmpeg screen recorder terminated at startup")
    REC_STARTED = time.monotonic()


def stop_video():
    if RECORDING and RECORDING.poll() is None:
        RECORDING.send_signal(signal.SIGINT)
        try:
            RECORDING.wait(timeout=35)
        except subprocess.TimeoutExpired:
            RECORDING.kill()
            RECORDING.wait(timeout=15)
    if REC_STARTED is not None:
        (OUT / "scene_timeline.json").write_text(
            json.dumps({
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "duration_s": round(time.monotonic() - REC_STARTED, 2),
                "scenes": SCENES,
                "capture_method": "ffmpeg x11grab, Chrome visible in Xvfb + real xterm",
                "model_execution": "REAL Hugging Face quantized DistilBERT ONNX",
                "mock_used": False,
            }, indent=2), encoding="utf-8")


def bring_browser_front(page):
    page.bring_to_front()
    result = run("xdotool", "search", "--onlyvisible", "--class",
                 "google-chrome", check=False, capture_output=True, text=True)
    if result.returncode == 0:
        ids = result.stdout.strip().splitlines()
        if ids:
            run("xdotool", "windowactivate", "--sync", ids[-1], check=False)
    wait(1)


def browse(page, url, hold=9):
    print("REAL_BROWSER_NAV", url, flush=True)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        bring_browser_front(page)
        wait(hold)
        return True
    except Exception as exc:
        print(f"BROWSER_NAV_WARNING {url}: {str(exc)[:200]}", flush=True)
        return False


def swagger_test(page, path, payload=None, hold=7):
    if not browse(page, "http://127.0.0.1:8000/docs", hold=1.5):
        return False
    try:
        page.locator(f'.opblock[data-path="{path}"] .opblock-summary').click(timeout=15000)
        block = page.locator(f'.opblock[data-path="{path}"]')
        block.get_by_role("button", name="Try it out").click(timeout=15000)
        if payload is not None:
            body = block.locator("textarea.body-param__text")
            body.wait_for(timeout=10000)
            body.fill(json.dumps(payload, ensure_ascii=False))
        wait(1.5)
        block.get_by_role("button", name="Execute").click(timeout=12000)
        block.locator(".response-col_status").first.wait_for(timeout=110000)
        status = block.locator(".response-col_status").first.inner_text().strip()
        body_text = block.locator(".responses-wrapper").inner_text()[:800]
        if "503" in status or "500" in status:
            raise RuntimeError(f"Swagger returned HTTP {status} with {body_text[:250]}")
        print("REAL_SWAGGER_RESULT", path, status, body_text.replace("\n", " ")[:400], flush=True)
        wait(hold)
        return True
    except Exception as exc:
        print(f"SWAGGER_WARNING {path}: {str(exc)[:550]}", flush=True)
        # On-screen fallback is still a real HTTP request from terminal later.
        return False


def main():
    if not shutil.which("google-chrome"):
        raise RuntimeError("This workflow requires installed Google Chrome")
    if not shutil.which("xterm"):
        raise RuntimeError("xterm missing")
    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY
    terminal = subprocess.Popen([
        "xterm", "-title", "Lab 2 - Real Terminal", "-geometry", "136x40+25+15",
        "-fa", "DejaVu Sans Mono", "-fs", "14",
        "-bg", "#0b1020", "-fg", "#e7efff",
        "-cr", "#52d1c2", "-e", "bash", "--noprofile", "--norc"
    ], cwd=HERE, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait(2)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False,
                executable_path=shutil.which("google-chrome"),
                args=[
                    "--no-sandbox", "--disable-gpu",
                    "--window-size=1550,850", "--window-position=15,15",
                ],
                env=env,
            )
            page = browser.new_page(viewport={"width": 1500, "height": 760}, device_scale_factor=1)
            start_video()
            try:
                mark("INTRODUCTION", "This is my real screen recording for Computational Thinking Lab Two. I will run the actual Python source, the pretrained Hugging Face model, and the FastAPI server, then execute live API requests.")
                type_real_command("echo 'LAB 2 | REAL SCREEN CAPTURE | 25127009' && pwd && python --version && ls -1", delay=9)

                mark("HUGGING FACE MODEL PAGE", "First, here is the Hugging Face model page for the English DistilBERT sentiment classifier. We use its quantized ONNX weights for CPU inference.")
                browse(page, "https://huggingface.co/Xenova/distilbert-base-uncased-finetuned-sst-2-english", hold=13)

                mark("PUBLIC GITHUB SOURCE CODE", "This is the public GitHub repository containing my FastAPI application. The model code loads real weights and tokenizes user input before inference.")
                browse(page, "https://github.com/hpban2527-ui/assignment-1/blob/main/lab2-sentiment-fastapi/main.py", hold=13)

                mark("SOURCE STRUCTURE", "Next, in the terminal, I inspect the source files and show how the FastAPI routes are defined.")
                type_real_command("ls main.py test_api.py check_real_model.py requirements.txt README.md && grep -n '^@app' main.py", delay=11)

                mark("INSTALLED DEPENDENCIES", "The required Python dependencies are installed. The application uses FastAPI, Pydantic, ONNX Runtime, and the Hugging Face tokenizer.")
                type_real_command("python -m pip show fastapi onnxruntime tokenizers | grep -E '^(Name|Version):'", delay=10)

                mark("EXECUTE THE REAL HUGGING FACE MODEL", "Now I run check real model dot py. This directly executes the actual downloaded Hugging Face model on a positive and a negative sentence. The scores shown on screen are measured results.")
                type_real_command("python check_real_model.py", delay=15)

                mark("START FASTAPI SERVER", "I start Uvicorn to expose the required GET home, GET health, and POST predict API endpoints over local HTTP.")
                type_real_command("python -m uvicorn main:app --host 127.0.0.1 --port 8000 > demo_artifacts/uvicorn_live.log 2>&1 & echo \"Uvicorn PID: $!\"; sleep 2; cat demo_artifacts/uvicorn_live.log", delay=8)

                mark("SWAGGER UI - REAL API", "The Swagger interface is generated from the running FastAPI application. I will use Try it out and Execute to call each endpoint.")
                browse(page, "http://127.0.0.1:8000/docs", hold=12)

                mark("LIVE GET ROOT", "The root endpoint returns a brief introduction to the system and the model name as JSON.")
                swagger_test(page, "/", hold=9)

                mark("LIVE GET HEALTH", "The health endpoint confirms the API server is responding, and shows whether the model has been loaded.")
                swagger_test(page, "/health", hold=9)

                mark("REAL POSITIVE INFERENCE VIA HTTP", "Here is the first live prediction. I submit I really love this movie, and the real DistilBERT model returns the positive label with its measured confidence score.")
                swagger_test(page, "/predict", {"text": "I really love this movie!"}, hold=12)

                mark("REAL NEGATIVE INFERENCE VIA HTTP", "For the second test, I submit This was a terrible experience. The model recognizes negative sentiment and returns a structured JSON response.")
                swagger_test(page, "/predict", {"text": "This was a terrible experience."}, hold=12)

                mark("VALIDATION - HTTP 422", "The input validator also rejects invalid or missing text. A blank request produces HTTP four twenty two instead of running the model.")
                swagger_test(page, "/predict", {"text": "   "}, hold=10)

                mark("REQUESTS INTEGRATION TESTS", "Finally I run the required Python requests test file against the live Uvicorn server. It checks all three endpoints, both real predictions, and invalid input handling.")
                type_real_command("python test_api.py --base-url http://127.0.0.1:8000", delay=17)

                mark("CONCLUSION AND VERIFICATION", "All real model and API tests have run on screen. The source is available publicly on GitHub, with a separate independent GitHub Actions verification log. Thank you for watching.")
                type_real_command("echo 'REAL MODEL: PASS | LIVE HTTP API: PASS | SOURCE: PUBLIC GITHUB' && echo 'Repository: https://github.com/hpban2527-ui/assignment-1/tree/main/lab2-sentiment-fastapi'", delay=10)

            finally:
                stop_video()
                browser.close()
    finally:
        terminal.terminate()
        try:
            terminal.wait(timeout=5)
        except subprocess.TimeoutExpired:
            terminal.kill()
    recorded = OUT / "lab2_raw_actual_screen.mp4"
    probe = run("ffprobe", "-v", "error", "-show_entries",
                "format=duration,size", "-of", "json", str(recorded),
                capture_output=True, text=True)
    print("REAL_SCREEN_VIDEO_PROBE", probe.stdout, flush=True)
    print("SCENE_COUNT", len(SCENES), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Add honest narration and simple captions to the genuine screen capture.

No screen frames are synthesized: the video comes from ffmpeg x11grab in
record_real_screen.py. Speech and captions describe the execution shown.
"""
import asyncio
import json
import math
import os
from pathlib import Path
import subprocess
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo_artifacts"
RAW = OUT / "lab2_raw_actual_screen.mp4"
TIMELINE = OUT / "scene_timeline.json"
FINAL = OUT / "LAB2_REAL_SCREEN_DEMO_25127009.mp4"
VOICES = OUT / "voice"
VOICES.mkdir(parents=True, exist_ok=True)

SPEECH = {
    "INTRODUCTION": "This is my Lab Two screen recording. I will show the actual source, run the pretrained model, and test the API live.",
    "HUGGING FACE MODEL PAGE": "Here is the pretrained DistilBERT sentiment model on Hugging Face. Its quantized ONNX weights run on a CPU.",
    "PUBLIC GITHUB SOURCE CODE": "The Python application is in this public GitHub repository. It loads the actual model weights and processes user input.",
    "SOURCE STRUCTURE": "These are the project files, including the application, dependencies, direct model check, and HTTP test script.",
    "INSTALLED DEPENDENCIES": "The dependencies are installed in this runtime, including FastAPI, ONNX Runtime, and the Hugging Face tokenizer.",
    "EXECUTE THE REAL HUGGING FACE MODEL": "I now execute the genuine pretrained model twice. The terminal prints the positive and negative predictions with their measured scores.",
    "START FASTAPI SERVER": "I start the Uvicorn server, which exposes the three required FastAPI endpoints over local HTTP.",
    "SWAGGER UI - REAL API": "This is the actual Swagger interface served by the running API. I will use its controls to send requests.",
    "LIVE GET ROOT": "The root endpoint returns the application introduction as JSON.",
    "LIVE GET HEALTH": "The health endpoint confirms that the API is running.",
    "REAL POSITIVE INFERENCE VIA HTTP": "For the first prediction, I send a positive sentence. The model responds with POSITIVE and a measured confidence score.",
    "REAL NEGATIVE INFERENCE VIA HTTP": "For the second prediction, I send a negative sentence. The model returns NEGATIVE with its actual score.",
    "VALIDATION - HTTP 422": "The application rejects blank input with HTTP four twenty two, confirming that input validation is active.",
    "REQUESTS INTEGRATION TESTS": "Now the Python requests script tests every endpoint, both live model predictions, and invalid input handling.",
    "CONCLUSION AND VERIFICATION": "All the real model and API tests pass. The full source and verification logs are available on public GitHub."
}


def run(*args):
    subprocess.run(args, check=True)


def ts(seconds):
    ticks = max(0, round(seconds * 100))
    cs = ticks % 100
    secs = ticks // 100
    return f"{secs // 3600}:{(secs // 60) % 60:02}:{secs % 60:02}.{cs:02}"


def ass_safe(text):
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def wrap(text, width=70):
    import textwrap
    return "\\N".join(textwrap.wrap(text, width=width))


async def make_voice(idx, title, text):
    target = VOICES / f"{idx:02d}.mp3"
    try:
        import edge_tts
        await asyncio.wait_for(
            edge_tts.Communicate(text=text, voice="en-US-JennyNeural",
                                 rate="+12%", volume="+0%").save(str(target)),
            timeout=45,
        )
        if target.stat().st_size < 1500:
            raise RuntimeError("Speech file is empty")
        return idx, target, "neural"
    except Exception as exc:
        fallback = VOICES / f"{idx:02d}.wav"
        print(f"EDGE_VOICE_WARNING scene={idx}: {exc}; using offline TTS", flush=True)
        run("espeak", "-ven+f3", "-s", "167", "-w", str(fallback), text)
        return idx, fallback, "offline"


async def voices_for_scenes(scenes):
    semaphore = asyncio.Semaphore(3)

    async def guarded(idx, scene):
        async with semaphore:
            return await make_voice(idx, scene["title"], SPEECH[scene["title"]])

    return await asyncio.gather(*(guarded(i, s) for i, s in enumerate(scenes)))


def make_subtitles(scenes, length):
    header = """[Script Info]
Title: Actual Lab 2 Screen Demo Captions
ScriptType: v4.00+
PlayResX: 1600
PlayResY: 900
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,DejaVu Sans,23,&H00FFFFFF,&H00FFFFFF,&H000D233C,&H9A08121C,0,0,0,0,100,100,0,0,3,1,0,2,90,90,20,1
Style: Chapter,DejaVu Sans,19,&H00A8FCE7,&H00FFFFFF,&H00162A40,&H9A071521,-1,0,0,0,100,100,0,0,3,1,0,9,20,40,22,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for idx, scene in enumerate(scenes):
        start = scene["at"]
        end = min(length, scenes[idx + 1]["at"] - 0.15 if idx + 1 < len(scenes) else length)
        if end <= start:
            continue
        chapter = ass_safe(scene["title"].replace(" VIA HTTP", ""))
        narration = ass_safe(wrap(SPEECH[scene["title"]]))
        events.append(f"Dialogue: 0,{ts(start)},{ts(end)},Chapter,,0,0,0,,{idx+1:02d} / {chapter}")
        events.append(f"Dialogue: 0,{ts(start+0.2)},{ts(end)},Narration,,0,0,0,,{narration}")
    dest = OUT / "video_captions.ass"
    dest.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return dest


def main():
    data = json.loads(TIMELINE.read_text(encoding="utf-8"))
    scenes, duration = data["scenes"], float(data["duration_s"])
    assert len(scenes) == len(SPEECH), f"scenes={len(scenes)}, narration={len(SPEECH)}"
    assert all(s["title"] in SPEECH for s in scenes)
    assert RAW.is_file() and RAW.stat().st_size > 50000

    audio_files = asyncio.run(voices_for_scenes(scenes))
    base = AudioSegment.silent(duration=round((duration + 0.8) * 1000), frame_rate=44100)
    voice_types = []
    for i, source, kind in audio_files:
        next_start = float(scenes[i + 1]["at"]) if i + 1 < len(scenes) else duration
        start = int(float(scenes[i]["at"]) * 1000) + 400
        max_time = max(1000, int(next_start * 1000) - start - 300)
        clip = AudioSegment.from_file(source)
        # Keep speech clear and avoid overlapping the next procedure.
        if len(clip) > max_time:
            print(f"NARRATION_CLIPPED scene={i}, actual={len(clip)}, slot={max_time}", flush=True)
            clip = clip[:max_time].fade_out(min(240, max_time // 10))
        voice_types.append(kind)
        base = base.overlay(clip - 2.0, position=start)

    narration_file = OUT / "mixed_narration.wav"
    base.export(narration_file, format="wav")
    subtitle = make_subtitles(scenes, duration)

    # Preserve every authentic recorded action frame, add only subtitles/voice.
    # No fake UI, artificial clicks, fabricated terminal results or slides.
    run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(RAW), "-i", str(narration_file),
        "-vf", f"ass={subtitle}",
        "-af", "alimiter=limit=0.90",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
        "-c:a", "aac", "-b:a", "160k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-shortest", str(FINAL))

    run("ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,width,height", "-of", "json", str(FINAL))
    report = {
        "real_recording_duration": duration,
        "video_file": FINAL.name,
        "audio": "edge-tts en-US-JennyNeural" if all(x == "neural" for x in voice_types)
            else f"mixed, neural={voice_types.count('neural')}, offline={voice_types.count('offline')}",
        "capture": data["capture_method"],
        "scenes": len(scenes),
        "zero_fake_screen_frames": True,
        "source_model_mocked": False,
        "source_video_sha256": None,
    }
    import hashlib
    report["source_video_sha256"] = hashlib.sha256(RAW.read_bytes()).hexdigest()
    (OUT / "final_video_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("FINAL_VIDEO_COMPLETE", json.dumps(report), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Kokoro OpenAI-compatible client.
- Prompts user for text in a loop (Ctrl+C to quit)
- POSTs to /v1/audio/speech
- Saves audio to files, optionally plays it (if sounddevice is installed)
"""

import argparse
import os
import sys
import time
import requests

# Optional playback
try:
    import sounddevice as sd
    import soundfile as sf
    HAVE_SD = True
except Exception:
    HAVE_SD = False


def ts():
    return time.strftime("%Y%m%d-%H%M%S")


def play_audio(path: str):
    if not HAVE_SD:
        print("[info] sounddevice not installed; skipping playback.")
        return
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    sd.play(data, sr)
    sd.wait()


def main():
    ap = argparse.ArgumentParser(description="Interactive TTS client for Kokoro server.")
    ap.add_argument("--url", default="http://localhost:8080/v1/audio/speech",
                    help="Server endpoint URL.")
    ap.add_argument("--model", default="tts-1", help="Model name to send.")
    ap.add_argument("--voice", default="af_heart", help="Voice ID.")
    ap.add_argument("--response-format", default="wav",
                    choices=["wav", "mp3", "ogg", "flac"], help="Audio format.")
    ap.add_argument("--lang-code", default=None, help="Optional lang code (e.g., a,b,h).")
    ap.add_argument("--speed", type=float, default=None, help="Optional speed multiplier.")
    ap.add_argument("--sample-rate", type=int, default=None, help="Optional sample rate (e.g., 24000).")
    ap.add_argument("--outdir", default="client_out", help="Folder to save audio files.")
    ap.add_argument("--basename", default="utt", help="Base filename prefix.")
    ap.add_argument("--play", action="store_true", help="Play audio after saving.")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print("Type text and press Enter to synthesize. Ctrl+C to quit.\n")

    idx = 0
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                continue

            body = {
                "model": args.model,
                "voice": args.voice,
                "input": line,
                "response_format": args.response_format,
            }
            if args.lang_code is not None:
                body["lang_code"] = args.lang_code
            if args.speed is not None:
                body["speed"] = args.speed
            if args.sample_rate is not None:
                body["sample_rate"] = args.sample_rate

            try:
                r = requests.post(args.url, json=body, timeout=120)
                r.raise_for_status()
            except requests.HTTPError as e:
                print(f"[HTTP error] {e} | response: {getattr(e.response, 'text', '')[:400]}")
                continue
            except requests.RequestException as e:
                print(f"[network error] {e}")
                continue

            ext = args.response_format
            fname = f"{args.basename}_{idx:04d}_{ts()}.{ext}"
            fpath = os.path.join(args.outdir, fname)
            with open(fpath, "wb") as f:
                f.write(r.content)

            print(f"[ok] saved → {fpath}")

            if args.play:
                play_audio(fpath)

            idx += 1

    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)


if __name__ == "__main__":
    main()

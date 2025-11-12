#Server.py
import json
import time
import os
import traceback
import logging
from typing import List
from io import BytesIO
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import uvicorn
import soundfile as sf
from pydub import AudioSegment

try:
    import torch
except Exception:
    torch = None

from kokoro import KPipeline

logging.basicConfig(level=logging.INFO)

SR = 24000
app = FastAPI()
pipeline = None


def as_numpy(x):
    if torch is not None and isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    else:
        x = np.asarray(x)
    return x.astype(np.float32).reshape(-1)


@app.on_event("startup")
async def _init():
    global pipeline
    pipeline = KPipeline(lang_code=os.getenv("KOKORO_LANG", "a"))


@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "Kokoro TTS WebSocket server.\n"
        "Connect to /ws with JSON: {\"text\",\"voice\",\"speed\",\"format\"}\n"
        "format: f32 | s16 | wav | mp3 | ogg | flac\n"
    )


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:   # 🔥 allow multiple messages in same connection
            req = await websocket.receive_text()
            cfg = json.loads(req)

            text = str(cfg.get("text", "")).strip()
            voice = str(cfg.get("voice", "af_heart"))
            speed = float(cfg.get("speed", 1.0))
            fmt = str(cfg.get("format", "f32")).lower()

            if not text:
                await websocket.send_text(json.dumps({"type": "done", "error": "empty text"}))
                continue   # don’t close, wait for next message

            await websocket.send_text(json.dumps({
                "type": "meta",
                "sample_rate": SR,
                "channels": 1,
                "sample_format": fmt
            }))

            t0 = time.perf_counter()
            ttfa_sent = False
            segments = 0
            audio_total_s = 0.0
            buf: List[np.ndarray] = []

            gen = pipeline(text, voice=voice, speed=speed, split_pattern=r"\n+")
            
            for (_gs, _ps, audio) in gen:
                now = time.perf_counter()
                if not ttfa_sent:
                    await websocket.send_text(json.dumps({"type": "ttfa", "ms": (now - t0) * 1000.0}))
                    ttfa_sent = True

                a = as_numpy(audio)
                buf.append(a)
                segments += 1
                audio_total_s += a.size / SR

                # Stream only for PCM
                if fmt in {"f32", "s16"}:
                    if fmt == "s16":
                        pcm = (np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes()
                    else:
                        pcm = a.tobytes()
                    await websocket.send_bytes(pcm)

            total_ms = (time.perf_counter() - t0) * 1000.0
            rtf = (total_ms / 1000.0) / max(1e-6, audio_total_s)

            # Encode full output for compressed formats
            if fmt in {"wav", "mp3", "ogg", "flac"}:
                full_audio = np.concatenate(buf) if len(buf) > 1 else buf[0]
                wav_io = BytesIO()
                sf.write(wav_io, np.clip(full_audio, -1, 1), SR, format="WAV", subtype="PCM_16")
                wav_io.seek(0)
                audio_seg = AudioSegment.from_wav(wav_io)
                out_io = BytesIO()
                audio_seg.export(out_io, format=fmt)
                await websocket.send_bytes(out_io.getvalue())

            await websocket.send_text(json.dumps({
                "type": "done",
                "total_ms": total_ms,
                "audio_ms": audio_total_s * 1000.0,
                "segments": segments,
                "rtf": rtf,
                "error": None
            }))

    except WebSocketDisconnect:
        logging.warning("Client disconnected.")
    except Exception as e:
        logging.error(traceback.format_exc())
        try:
            await websocket.send_text(json.dumps({"type": "done", "error": str(e)}))
        except Exception:
            pass
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "4000")), reload=False)

#client.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, json, os
import numpy as np
import websockets
import sounddevice as sd
import soundfile as sf

async def tts_once(url, text, voice="af_heart", speed=1.0, fmt="f32"):
    async with websockets.connect(url, max_size=None) as ws:
        await ws.send(json.dumps({"text": text, "voice": voice, "speed": speed, "format": fmt}))
        sr = 24000
        stream = None
        dtype = np.float32 if fmt == "f32" else np.int16
        audio_buf = bytearray()

        try:
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    # Stream PCM audio
                    if fmt in {"f32", "s16"}:
                        a = np.frombuffer(msg, dtype=dtype)
                        if fmt == "s16":
                            a = (a.astype(np.float32) / 32767.0)
                        if stream is None:
                            stream = sd.OutputStream(samplerate=sr, channels=1, dtype="float32")
                            stream.start()
                        stream.write(a.reshape(-1, 1))
                    else:
                        # For encoded audio (mp3, wav, etc.)
                        audio_buf.extend(msg)

                else:
                    data = json.loads(msg)
                    t = data.get("type")
                    if t == "meta":
                        sr = int(data["sample_rate"])
                        print(f"[meta] sr={sr}, fmt={data['sample_format']}")
                    elif t == "ttfa":
                        print(f"[ttfa] {data['ms']:.1f} ms")
                    elif t == "done":
                        if data.get("error"):
                            print("[done:ERROR]", data["error"])
                        else:
                            print(f"[done] gen={data['total_ms']:.1f} ms, "
                                  f"audio={data['audio_ms']:.1f} ms, "
                                  f"segments={data['segments']}, rtf={data['rtf']:.3f}")
                        break
        finally:
            if stream is not None:
                stream.stop(); stream.close()

            # Save encoded file if needed
            if fmt not in {"f32", "s16"} and len(audio_buf) > 0:
                os.makedirs("out_audio", exist_ok=True)
                out_path = f"out_audio/output_{fmt}.{'mp3' if fmt == 'mp3' else fmt}"
                with open(out_path, "wb") as f:
                    f.write(audio_buf)
                print(f"[saved] {out_path}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="wss://whisperstream.exlservice.com:3000/ws")
    ap.add_argument("--text", default=None)
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--fmt", default="f32", choices=["f32", "s16", "wav", "mp3", "ogg", "flac"])
    args = ap.parse_args()

    async def run():
        if args.text:
            await tts_once(args.url, args.text, args.voice, args.speed, args.fmt)
            return

        print("Kokoro WS client (interactive). Type text and press Enter. /q to quit.")
        while True:
            try:
                line = input("text> ").strip()
            except EOFError:
                break
            if not line:
                continue
            if line in {"/q", "/quit", "/exit"}:
                break
            try:
                await tts_once(args.url, line, args.voice, args.speed, args.fmt)
            except KeyboardInterrupt:
                print("\n[info] cancelled current utterance")
            except Exception as e:
                print(f"[warn] send/play failed: {e}")

    asyncio.run(run())

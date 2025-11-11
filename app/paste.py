client.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio, json
import numpy as np
import websockets
import sounddevice as sd

async def tts_once(url, text, voice="af_heart", speed=1.0, fmt="f32"):
    async with websockets.connect(url, max_size=None) as ws:
        await ws.send(json.dumps({"text": text, "voice": voice, "speed": speed, "format": fmt}))
        sr = 24000
        stream = None
        dtype = np.float32 if fmt == "f32" else np.int16
        try:
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    a = np.frombuffer(msg, dtype=dtype)
                    if fmt == "s16":  # convert to float for playback
                        a = (a.astype(np.float32) / 32767.0)
                    if stream is None:
                        stream = sd.OutputStream(samplerate=sr, channels=1, dtype="float32")
                        stream.start()
                    stream.write(a.reshape(-1, 1))
                else:
                    data = json.loads(msg)
                    t = data.get("type")
                    if t == "meta":
                        sr = int(data["sample_rate"])
                        print(f"[meta] sr={sr}, fmt={data['sample_format']}")
                    elif t == "ttfa":
                        print(f"[ttfa] {data['ms']:.1f} ms")
                    elif t == "done":
                        if data.get("error"): print("[done:ERROR]", data["error"])
                        else:
                            print(f"[done] gen={data['total_ms']:.1f} ms, audio={data['audio_ms']:.1f} ms, "
                                  f"segments={data['segments']}, rtf={data['rtf']:.3f}")
                        break
        finally:
            if stream is not None:
                stream.stop(); stream.close()

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="wss://whisperstream.exlservice.com:3000/ws")
    ap.add_argument("--text", default=None, help="If provided, runs once with this text; otherwise interactive.")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--fmt", default="f32", choices=["f32","s16"])
    args = ap.parse_args()

    async def run():
        # Single-shot mode only if --text is provided
        if args.text is not None:
            await tts_once(args.url, args.text, args.voice, args.speed, args.fmt)
            return

        # Default: interactive mode (no flags needed)
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

#server.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, time, os, traceback
from typing import List
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import uvicorn
import logging

# Configure the basic settings
logging.basicConfig(level=logging.INFO)

try:
    import torch
except Exception:
    torch = None

from kokoro import KPipeline

SR = 24000
app = FastAPI()
pipeline = None  # lazy init for quick start

def as_numpy(x):
    if torch is not None and isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    else:
        x = np.asarray(x)
    return x.astype(np.float32).reshape(-1)

@app.on_event("startup")
async def _init():
    global pipeline
    # 'a' US-EN, 'b' UK-EN, 'h' Hindi, etc.
    pipeline = KPipeline(lang_code=os.getenv("KOKORO_LANG", "a"))

@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "Kokoro TTS WebSocket server.\n"
        "Connect to /ws with JSON: {\"text\",\"voice\",\"speed\",\"format\"}\n"
        "format: \"f32\" (float32 PCM) or \"s16\" (int16 PCM)\n"
    )

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    """
    Client -> Server (JSON text frame):
      {"text":"Hello","voice":"af_heart","speed":1.0,"format":"f32|s16","save_wav":false}

    Server -> Client:
      {"type":"meta","sample_rate":24000,"channels":1,"sample_format":"f32|s16"}
      {"type":"ttfa","ms": <float>}
      <binary frames>  # raw PCM per chunk (float32 if f32, int16 if s16)
      {"type":"done","total_ms":..,"audio_ms":..,"segments":..,"rtf":..,"error":null}
    """
    await websocket.accept()
    try:
        req = await websocket.receive_text()
        cfg = json.loads(req)

        text  = str(cfg.get("text", "")).strip()
        voice = str(cfg.get("voice", "af_heart"))
        speed = float(cfg.get("speed", 1.0))
        fmt   = str(cfg.get("format", "f32")).lower()  # "f32" default, or "s16"
        save_wav = bool(cfg.get("save_wav", False))

        if not text:
            await websocket.send_text(json.dumps({"type":"done","error":"empty text"}))
            await websocket.close()
            return

        await websocket.send_text(json.dumps({
            "type":"meta", "sample_rate": SR, "channels": 1, "sample_format": fmt
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
                await websocket.send_text(json.dumps({"type":"ttfa","ms": (now - t0) * 1000.0}))
                ttfa_sent = True

            a = as_numpy(audio)
            audio_total_s += a.size / SR
            segments += 1
            buf.append(a)

            if fmt == "s16":
                pcm = (np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes()
            else:
                pcm = a.tobytes()  # float32
            await websocket.send_bytes(pcm)

        total_ms = (time.perf_counter() - t0) * 1000.0
        rtf = (total_ms / 1000.0) / max(1e-6, audio_total_s)

        if save_wav and buf:
            try:
                import soundfile as sf
                os.makedirs("out_wavs", exist_ok=True)
                full = np.concatenate(buf) if len(buf) > 1 else buf[0]
                sf.write(f"out_wavs/{int(time.time())}.wav", np.clip(full, -1, 1), SR, subtype="PCM_16")
            except Exception:
                pass

        await websocket.send_text(json.dumps({
            "type":"done",
            "total_ms": total_ms,
            "audio_ms": audio_total_s * 1000.0,
            "segments": segments,
            "rtf": rtf,
            "error": None
        }))
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    uvicorn.run("ws_kokoro_server:app", host="0.0.0.0", port=int(os.getenv("PORT","4000")), reload=False)

#dockerfile
FROM python:3.12-slim

ENV https_proxy="http://163.116.128.80:8080"
ENV http_proxy="http://163.116.128.80:8080"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Language for KPipeline: a=US-EN, b=UK-EN, h=Hindi, etc.
ENV KOKORO_LANG=a

CMD ["uvicorn", "ws_kokoro_server:app", "--host", "0.0.0.0", "--port", "4000"]

#requirements.txt
fastapi
kokoro
numpy
pandas
psutil
soundfile
sounddevice
torch
uvicorn
websockets

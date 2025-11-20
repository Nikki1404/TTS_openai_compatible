gemini:
  api_key: "YOUR_REAL_GEMINI_API_KEY_HERE"
  model: "gemini-2.5-flash-preview-tts"

audio:
  default_voice: "Kore"
  sample_rate: 24000
  output_dir: "outputs"



import struct


def l16_to_wav(l16_bytes: bytes, sample_rate=24000, num_channels=1):
    bits_per_sample = 16
    block_align = num_channels * bits_per_sample // 8
    byte_rate = sample_rate * block_align
    data_size = len(l16_bytes)
    file_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        file_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + l16_bytes


def linear2ulaw(sample):
    MULAW_MAX = 0x1FFF
    MULAW_BIAS = 33
    sign = (sample >> 8) & 0x80

    if sign != 0:
        sample = -sample
    if sample > MULAW_MAX:
        sample = MULAW_MAX

    sample += MULAW_BIAS

    exponent = 7
    exp_mask = 0x4000
    while (sample & exp_mask) == 0 and exponent > 0:
        exponent -= 1
        exp_mask >>= 1

    mantissa = (sample >> (exponent + 3)) & 0x0F
    ulaw_byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
    return ulaw_byte


def l16_to_mulaw(l16_bytes):
    out = bytearray()
    for i in range(0, len(l16_bytes), 2):
        sample = struct.unpack("<h", l16_bytes[i:i+2])[0]
        out.append(linear2ulaw(sample))
    return bytes(out)


import os
import re
import datetime


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_filename(prefix, voice, text, ext="wav"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    preview = re.sub(r"[^A-Za-z0-9]+", "_", text[:12])
    return f"{prefix}_{voice}_{preview}_{timestamp}.{ext}"


import requests
import base64
import time
import yaml
from .audio_utils import l16_to_wav, l16_to_mulaw
from .file_utils import ensure_dir, generate_filename


class GeminiTTS:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        self.api_key = cfg["gemini"]["api_key"]
        self.model = cfg["gemini"]["model"]
        self.default_voice = cfg["audio"]["default_voice"]
        self.sample_rate = cfg["audio"]["sample_rate"]
        self.output_dir = cfg["audio"]["output_dir"]

        ensure_dir(self.output_dir)

        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

    def synthesize(self, text, voice=None):
        if voice is None:
            voice = self.default_voice

        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": text}]}
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": voice}
                    }
                }
            }
        }

        # ------ Start API latency timer ------
        t_start = time.time()
        response = requests.post(self.url, json=payload)
        t_api = time.time()

        if response.status_code != 200:
            raise RuntimeError(response.text)

        data = response.json()
        inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]

        raw_l16 = base64.b64decode(inline["data"])

        # ------ WAV ------
        t_wav_start = time.time()
        wav_bytes = l16_to_wav(raw_l16, self.sample_rate)
        t_wav_end = time.time()

        wav_path = f"{self.output_dir}/{generate_filename('tts_wav', voice, text, 'wav')}"
        with open(wav_path, "wb") as f:
            f.write(wav_bytes)

        # ------ MULAW ------
        t_mulaw_start = time.time()
        mulaw_bytes = l16_to_mulaw(raw_l16)
        t_mulaw_end = time.time()

        mulaw_path = f"{self.output_dir}/{generate_filename('tts_mulaw', voice, text, 'mulaw')}"
        with open(mulaw_path, "wb") as f:
            f.write(mulaw_bytes)

        t_end = time.time()

        return {
            "wav_path": wav_path,
            "mulaw_path": mulaw_path,
            "latency": {
                "api_ms": round((t_api - t_start) * 1000, 2),
                "wav_encode_ms": round((t_wav_end - t_wav_start) * 1000, 2),
                "mulaw_encode_ms": round((t_mulaw_end - t_mulaw_start) * 1000, 2),
                "total_ms": round((t_end - t_start) * 1000, 2),
            }
        }



from tts.gemini_client import GeminiTTS

if __name__ == "__main__":
    client = GeminiTTS()

    print("=== Gemini TTS Interactive Mode ===")
    print("Type text and press Enter (type 'exit' to quit)\n")

    while True:
        text = input("Enter text: ").strip()
        if text.lower() == "exit":
            break

        voice = input("Choose voice (default Kore): ").strip()
        if voice == "":
            voice = None

        result = client.synthesize(text, voice)

        print("\n======= LATENCY REPORT =======")
        for k, v in result["latency"].items():
            print(f"{k}: {v} ms")

        print("\nSaved:")
        print("WAV   →", result["wav_path"])
        print("MULAW →", result["mulaw_path"])
        print("==============================\n")



requests
pyyaml


# syntax=docker/dockerfile:1.4

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["python", "main.py"]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import os
import traceback
import logging
from typing import List
from io import BytesIO
from datetime import datetime
import numpy as np
import yaml
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

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

logging.basicConfig(level=CONFIG["logging"]["level"])

SR = CONFIG["sample_rate"]
app = FastAPI()
pipeline = None

# -------- NEW: chunking config helpers --------
CHUNKING_CFG = CONFIG.get("chunking", {})
CHUNK_ENABLED = CHUNKING_CFG.get("enabled", True)
WORD_THRESHOLD_DEFAULT = int(CHUNKING_CFG.get("word_threshold", 20))

def chunk_text(text: str, max_words: int | None = None) -> list[str]:
    """
    Split long text into smaller chunks for better latency.
    - First split by sentence.
    - If still long, break into ~max_words word slices.
    """
    if max_words is None:
        max_words = WORD_THRESHOLD_DEFAULT

    words = text.split()
    if len(words) <= max_words:
        return [text]

    import re
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks: list[str] = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        ws = s.split()
        if len(ws) <= max_words:
            chunks.append(s)
        else:
            for i in range(0, len(ws), max_words):
                chunks.append(" ".join(ws[i:i + max_words]))
    return chunks
# ----------------------------------------------


def as_numpy(x):
    """Convert tensors to numpy arrays."""
    if torch is not None and isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    else:
        x = np.asarray(x)
    return x.astype(np.float32).reshape(-1)


# -------- NEW: device selection for CUDA --------
def get_device() -> str:
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"
# -----------------------------------------------


@app.on_event("startup")
async def _init():
    """Initialize Kokoro TTS pipeline."""
    global pipeline
    device = get_device()  # NEW
    pipeline = KPipeline(lang_code=CONFIG["lang_code"], device=device)  # UPDATED
    logging.info(
        f"✅ Kokoro pipeline initialized (lang={CONFIG['lang_code']}, device={device})"
    )


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
    logging.info("connection open")
    try:
        while True:
            req = await websocket.receive_text()
            cfg = json.loads(req)

            text = str(cfg.get("text", "")).strip()
            voice = str(cfg.get("voice", CONFIG["voice"]))
            speed = float(cfg.get("speed", CONFIG["speed"]))
            fmt = str(cfg.get("format", CONFIG["format"])).lower()

            if not text:
                await websocket.send_text(json.dumps({"type": "done", "error": "empty text"}))
                continue

            # -------- NEW: chunking decision --------
            word_count = len(text.split())
            if CHUNK_ENABLED and word_count > WORD_THRESHOLD_DEFAULT:
                chunks = chunk_text(text)
                logging.info(
                    f"Chunking enabled: {word_count} words → {len(chunks)} chunk(s) "
                    f"(threshold={WORD_THRESHOLD_DEFAULT})"
                )
            else:
                chunks = [text]
            # ----------------------------------------

            await websocket.send_text(json.dumps({
                "type": "meta",
                "sample_rate": SR,
                "channels": 1,
                "sample_format": fmt
            }))

            start_time = time.time()
            start_human = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            logging.info(f"[start] {start_human}")

            t0 = time.perf_counter()
            ttfa_sent = False
            segments = 0
            audio_total_s = 0.0
            buf: List[np.ndarray] = []

            # -------- UPDATED: run pipeline per chunk, keep old logic inside --------
            for chunk_idx, chunk_text_part in enumerate(chunks):
                gen = pipeline(
                    chunk_text_part,
                    voice=voice,
                    speed=speed,
                    split_pattern=CONFIG["pipeline"]["split_pattern"],
                )

                for (_gs, _ps, audio) in gen:
                    now = time.perf_counter()
                    if not ttfa_sent:
                        await websocket.send_text(json.dumps(
                            {"type": "ttfa", "ms": (now - t0) * 1000.0}))
                        ttfa_sent = True

                    a = as_numpy(audio)
                    buf.append(a)
                    segments += 1
                    audio_total_s += a.size / SR

                    # streaming path (minimal post-processing)
                    if fmt in {"f32", "s16"}:
                        if fmt == "s16":
                            pcm = (np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes()
                        else:
                            pcm = a.tobytes()
                        await websocket.send_bytes(pcm)
            # ---------------------------------------------------------------

            total_ms = (time.perf_counter() - t0) * 1000.0
            rtf = (total_ms / 1000.0) / max(1e-6, audio_total_s)

            end_time = time.time()
            end_human = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            total_time_sec = end_time - start_time

            logging.info(f"[end]   {end_human}")
            logging.info(f"[total] {total_time_sec:.9f} sec")  # full microsecond precision

            # Encoded formats: keep behaviour, but reduce work for WAV
            if fmt in {"wav", "mp3", "ogg", "flac"}:
                full_audio = np.concatenate(buf) if len(buf) > 1 else buf[0]
                wav_io = BytesIO()
                sf.write(
                    wav_io,
                    np.clip(full_audio, -1, 1),
                    SR,
                    format="WAV",
                    subtype="PCM_16",
                )
                wav_io.seek(0)

                if fmt == "wav":
                    # -------- NEW: avoid extra pydub encode for WAV --------
                    await websocket.send_bytes(wav_io.getvalue())
                else:
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
                "error": None,
                "start_time": start_time,
                "end_time": end_time,
                "total_time_sec": total_time_sec
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
    finally:
        logging.info("connection closed")


if __name__ == "__main__":
    uvicorn.run(
        "ws_kokoro_server:app",
        host=CONFIG["server"]["host"],
        port=int(CONFIG["server"]["port"]),
        reload=CONFIG["server"]["reload"]
    )


#Dockerfile 
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
        python3.12 \
        python3.12-distutils \
        python3.12-venv \
        ffmpeg \
        build-essential gcc g++ make \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*


RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

WORKDIR /app

COPY . /app/

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install -r /app/requirements.txt


ENV KOKORO_LANG=a
EXPOSE 4000

CMD ["python3", "ws_kokoro_server:app", "--host", "0.0.0.0", "--port", "4000"]


logging:
  level: INFO

server:
  host: "0.0.0.0"
  port: 4000
  reload: false

sample_rate: 24000
lang_code: "a"
voice: "af_heart"
speed: 1.0
format: "f32"

pipeline:
  split_pattern: "([.!?])"

chunking:
  enabled: true
  word_threshold: 20


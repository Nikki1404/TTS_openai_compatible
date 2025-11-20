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


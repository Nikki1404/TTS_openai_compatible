import { TTSService } from '../interfaces/TTSService';
import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';
import logger from '../../common/logger';

export class GoogleTTSService implements TTSService {
    private client: TextToSpeechClient;
    private breaker: CircuitBreaker;

    constructor() {
        const projectId = process.env.GOOGLE_PROJECT_ID || "emr-dgt-autonomous-uctr1-snbx";
        if (!projectId) {
            const errorMessage = 'GOOGLE_PROJECT_ID environment variable is not set.';
            logger.error(errorMessage);
            throw new Error(errorMessage);
        }

        const location = process.env.GOOGLE_LOCATION || 'global';
        const clientOptions = location === 'global' ? {} : { apiEndpoint: `${location}-texttospeech.googleapis.com` };
        this.client = new TextToSpeechClient({});
        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        try {
            logger.info({ text }, 'Synthesizing speech with Google TTS');
            const voiceName = process.env.GOOGLE_TTS_VOICE_NAME || 'en-US-Wavenet-D';
            const ssmlGender = (process.env.GOOGLE_TTS_VOICE_GENDER || 'MALE') as ('MALE' | 'FEMALE' | 'NEUTRAL' | 'SSML_VOICE_GENDER_UNSPECIFIED');
            const audioEncoding = (process.env.GOOGLE_TTS_VOICE_AUDIO_ENCODING || 'MULAW') as ('MULAW' | 'LINEAR16' | 'MP3' | 'OGG_OPUS' | 'ALAW' | 'PCM' | 'AUDIO_ENCODING_UNSPECIFIED');
            const sampleRateHertz = typeof process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ === 'string'
                ? parseInt(process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ, 10)
                : (process.env.GOOGLE_TTS_VOICE_SAMPLE_RATE_HERTZ || 8000);

            const isSSML = /<speak[\s>]|<prosody[\s>]|<break[\s>]|<emphasis[\s>]|<google:style[\s>]/i.test(text);
            const request = {
                input: isSSML ? { ssml: text } : { text },
                voice: {
                    languageCode: process.env.GOOGLE_TTS_VOICE_LANGUAGE_CODE || 'en_US',
                    name: voiceName,
                    ssmlGender: ssmlGender,
                },
                audioConfig: { audioEncoding: audioEncoding, sampleRateHertz: sampleRateHertz },
            };

            const [response] = await this.client.synthesizeSpeech(request);
            if (!response.audioContent) {
                throw new Error('No audio content in Google TTS response.');
            }
            return response.audioContent as Uint8Array;
        } catch (err) {
            logger.error({ err, text }, 'Error synthesizing speech with Google TTS');
            throw err;
        }
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}


#gemini-tts
import { TTSService } from '../interfaces/TTSService';
import { GoogleGenerativeAI } from '@google/generative-ai';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';

export class GeminiTTSService implements TTSService {
    private generativeAi: GoogleGenerativeAI;
    private breaker: CircuitBreaker;

    constructor() {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            throw new Error('Gemini API key not configured.');
        }
        this.generativeAi = new GoogleGenerativeAI(apiKey);
        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        const model = this.generativeAi.getGenerativeModel({ model: "gemini-1.5-flash-preview" });
        const result = await model.generateContent(text);
        const response = await result.response;
        // This is a placeholder for how to get the audio data.
        // The actual implementation will depend on the API response format.
        // For now, we'll assume the response has a method to get the audio as a Uint8Array.
        // Replace this with the actual method when the API is finalized.
        // const audio = await response.audio();
        // return new Uint8Array(audio);
        return new Uint8Array(); // Placeholder
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}

#google_auth-utils.js
"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getGoogleAuthToken = void 0;
const google_auth_library_1 = require("google-auth-library");
const logger_1 = __importDefault(require("../common/logger"));
let cachedToken = null;
/**
 * Generates a short-lived OAuth2 access token for Google Cloud APIs.
 * Caches the token in memory to avoid generating a new one for every session.
 */
async function getGoogleAuthToken() {
    // If we have a valid, non-expired token, return it.
    if (cachedToken && cachedToken.expiry > Date.now() + 60 * 1000) { // 60s buffer
        return cachedToken.token;
    }
    try {
        logger_1.default.info('Generating new Google Cloud auth token.');
        const auth = new google_auth_library_1.GoogleAuth({
            scopes: 'https://www.googleapis.com/auth/cloud-platform',
        });
        const accessToken = await auth.getAccessToken();
        if (!accessToken) {
            throw new Error('Failed to retrieve access token or expiry from Google Auth.');
        }
        cachedToken = {
            token: accessToken,
            expiry: Date.now() + (60 * 1000),
        };
        return cachedToken.token;
    }
    catch (err) {
        logger_1.default.error({ err }, 'Error generating Google Cloud auth token');
        throw err;
    }
}
exports.getGoogleAuthToken = getGoogleAuthToken;
//# sourceMappingURL=google-auth-utils.js.map

google-auth-utils.ts

import { GoogleAuth } from 'google-auth-library';
import logger from '../common/logger';

let cachedToken: { token: string; expiry: number } | null = null;

/**
 * Generates a short-lived OAuth2 access token for Google Cloud APIs.
 * Caches the token in memory to avoid generating a new one for every session.
 */
export async function getGoogleAuthToken(): Promise<string> {
    // If we have a valid, non-expired token, return it.
    if (cachedToken && cachedToken.expiry > Date.now() + 60 * 1000) { // 60s buffer
        return cachedToken.token;
    }

    try {
        logger.info('Generating new Google Cloud auth token.');
        const auth = new GoogleAuth({
            scopes: 'https://www.googleapis.com/auth/cloud-platform',
        });
        const accessToken = await auth.getAccessToken();

        if (!accessToken) {
            throw new Error('Failed to retrieve access token or expiry from Google Auth.');
        }

        cachedToken = {
            token: accessToken,
            expiry: Date.now() + (60 * 1000),
        };

        return cachedToken.token;
    } catch (err) {
        logger.error({ err }, 'Error generating Google Cloud auth token');
        throw err;
    }
}

#google_tts.py
import time
import datetime
import numpy as np
import sounddevice as sd
from google.cloud import texttospeech
import wave

client = texttospeech.TextToSpeechClient()

VOICE = "en-US-Wavenet-D"
LANG = "en-US"


# ---------------------- WAV HELPERS ----------------------
def save_wav_linear16(filename, audio_bytes, sample_rate=24000):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)


def play_linear16(audio_bytes, sample_rate=24000):
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    sd.play(audio_array, samplerate=sample_rate)
    sd.wait()


# ---------------------- MULAW HELPERS ----------------------
def play_mulaw(audio_bytes, sample_rate=8000):
    ulaw = np.frombuffer(audio_bytes, dtype=np.uint8)
    pcm = (ulaw.astype(np.float32) - 128) * 256
    pcm = pcm.astype(np.int16)
    sd.play(pcm, samplerate=sample_rate)
    sd.wait()


# -------------------------------------------------------
# Perform TTS + capture start/end timestamps
# -------------------------------------------------------
def tts_with_timestamps(text):
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=LANG,
        name=VOICE,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    # HIGH QUALITY WAV TEST --------------------------
    print("\n===== WAV (PLAYABLE AUDIO) =====")

    audio_config_wav = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000
    )

    # Timestamp before API call
    start_time = datetime.datetime.now()
    start_ts = time.time()

    resp_wav = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=voice_params,
        audio_config=audio_config_wav
    )

    # Timestamp after API call
    end_time = datetime.datetime.now()
    end_ts = time.time()

    latency_ms = (end_ts - start_ts) * 1000

    print(f"Start Time: {start_time}")
    print(f"End Time:   {end_time}")
    print(f"WAV Latency: {latency_ms:.2f} ms")

    save_wav_linear16("output.wav", resp_wav.audio_content)
    play_linear16(resp_wav.audio_content)


    # MULAW TELEPHONY TEST ----------------------------
    print("\n===== MULAW 8000 Hz (TELEPHONY) =====")

    audio_config_ulaw = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MULAW,
        sample_rate_hertz=8000
    )

    # Timestamp for CHUNK 2
    start_time2 = datetime.datetime.now()
    start_ts2 = time.time()

    resp_ulaw = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=voice_params,
        audio_config=audio_config_ulaw
    )

    end_time2 = datetime.datetime.now()
    end_ts2 = time.time()

    latency_ms2 = (end_ts2 - start_ts2) * 1000

    with open("output_mulaw.raw", "wb") as f:
        f.write(resp_ulaw.audio_content)

    print(f"Start Time: {start_time2}")
    print(f"End Time:   {end_time2}")
    print(f"MULAW Latency: {latency_ms2:.2f} ms")

    play_mulaw(resp_ulaw.audio_content)

    return latency_ms, latency_ms2


# -------------------------------------------------------
# INTERACTIVE LOOP
# -------------------------------------------------------
if __name__ == "__main__":
    print("===============================================")
    print("🔵 Google TTS Interactive Tester (with timestamps)")
    print("Type text and press ENTER to speak.")
    print("Type 'exit' to quit.")
    print("===============================================\n")

    while True:
        text = input("Enter text: ")

        if text.lower().strip() == "exit":
            print("\nExiting…")
            break

        if text.strip() == "":
            print("⚠️ Please enter valid text.")
            continue

        wav_lat, mulaw_lat = tts_with_timestamps(text)

        print("\n--------------- SUMMARY ----------------")
        print(f"WAV Latency:   {wav_lat:.2f} ms")
        print(f"MULAW Latency: {mulaw_lat:.2f} ms")
        print("-----------------------------------------\n")

export GOOGLE_APPLICATION_CREDENTIALS="service_account.json"
set GOOGLE_APPLICATION_CREDENTIALS=service_account.json
$env:GOOGLE_APPLICATION_CREDENTIALS="service_account.json"

#gemini-tts.py


import os
import time
import datetime
import base64
import json
from pathlib import Path

import requests


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

# Read API key from environment (recommended for security)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Set it first, e.g. in CMD:  set GEMINI_API_KEY=your_key_here"
    )

MODEL_NAME = "models/gemini-tts-1"      # Gemini TTS model
VOICE_NAME = "Pine"                     # Natural English voice
OUTPUT_FILE = "gemini_tts_output.wav"   # Output file name

API_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent"


# ------------------------------------------------------------
# FUNCTION: Call Gemini-TTS & measure pure API latency
# ------------------------------------------------------------
def call_gemini_tts(text: str):
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": text}
                ]
            }
        ],
        "generationConfig": {
            "audioConfig": {
                "voiceName": VOICE_NAME,
                "audioEncoding": "LINEAR16",
                "sampleRateHertz": 24000,
            }
        },
    }

    # ---- record high-precision start time ----
    start_datetime = datetime.datetime.now()
    start = time.perf_counter()  # high-res timer (ns → we convert to µs / ms)

    # HTTP POST to Gemini-TTS
    response = requests.post(
        API_URL,
        headers=headers,
        params={"key": API_KEY},  # API key passed as query param
        data=json.dumps(payload),
        timeout=30,
    )

    # ---- record end time ----
    end_datetime = datetime.datetime.now()
    end = time.perf_counter()

    # ---- basic error handling ----
    if response.status_code != 200:
        print(" API ERROR")
        print("Status:", response.status_code)
        print("Body  :", response.text)
        return None

    data = response.json()

    # Extract base64 audio data
    try:
        audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    except (KeyError, IndexError) as e:
        print(" Unexpected response format from Gemini:")
        print(json.dumps(data, indent=2))
        raise e

    # Decode to raw bytes
    audio_bytes = base64.b64decode(audio_b64)

    # Save file
    Path(OUTPUT_FILE).write_bytes(audio_bytes)

    # Latency calculations
    latency_seconds = end - start
    latency_ms = latency_seconds * 1000.0
    latency_us = latency_seconds * 1_000_000.0

    print("\n================ GEMINI TTS LATENCY REPORT ================")
    print(f"Text            : {text}")
    print(f"Start Time      : {start_datetime}")
    print(f"End Time        : {end_datetime}")
    print(f"Latency         : {latency_ms:.3f} ms ({latency_us:.0f} μs)")
    print(f"Audio Size      : {len(audio_bytes)} bytes")
    print(f"Saved File      : {OUTPUT_FILE}")
    print("===========================================================\n")

    return latency_ms, latency_us


# ------------------------------------------------------------
# INTERACTIVE LOOP
# ------------------------------------------------------------
def main():
    print("=====================================================")
    print(" Gemini-TTS Latency Tester (API Key)")
    print("• Type text and press ENTER to call Gemini-TTS")
    print("• A WAV file will be saved as gemini_tts_output.wav")
    print("• Type 'exit' to quit")
    print("=====================================================\n")

    while True:
        text = input("Enter text: ").strip()

        if text.lower() == "exit":
            print("Exiting…")
            break

        if not text:
            print("⚠ Please enter some text.")
            continue

        try:
            call_gemini_tts(text)
        except Exception as e:
            print("❌ Exception during TTS call:", e)


if __name__ == "__main__":
    main()


import { TTSService } from '../interfaces/TTSService';
import { GoogleGenerativeAI } from '@google/generative-ai';
import CircuitBreaker from 'opossum';
import { circuitBreakerOptions } from '../../common/circuit-breaker';

export class GeminiTTSService implements TTSService {
    private generativeAi: GoogleGenerativeAI;
    private breaker: CircuitBreaker;

    constructor() {
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            throw new Error('Gemini API key not configured.');
        }
        this.generativeAi = new GoogleGenerativeAI(apiKey);
        this.breaker = new CircuitBreaker(this.synthesizeSpeech.bind(this), circuitBreakerOptions);
    }

    private async synthesizeSpeech(text: string): Promise<Uint8Array> {
        const model = this.generativeAi.getGenerativeModel({ model: "gemini-1.5-flash-preview" });
        const result = await model.generateContent(text);
        const response = await result.response;
        // This is a placeholder for how to get the audio data.
        // The actual implementation will depend on the API response format.
        // For now, we'll assume the response has a method to get the audio as a Uint8Array.
        // Replace this with the actual method when the API is finalized.
        // const audio = await response.audio();
        // return new Uint8Array(audio);
        return new Uint8Array(); // Placeholder
    }

    synthesize(text: string): Promise<Uint8Array> {
        return this.breaker.fire(text) as Promise<Uint8Array>;
    }
}





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
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

# Thread pool for encoding
executor = ThreadPoolExecutor(max_workers=4)

# Chunking config
CHUNK_ENABLED = CONFIG.get("chunking", {}).get("enabled", True)
WORD_THRESHOLD = int(CONFIG.get("chunking", {}).get("word_threshold", 20))


def as_numpy(x):
    if torch is not None and isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy().astype(np.float32).reshape(-1)
    return np.asarray(x, dtype=np.float32).reshape(-1)

def get_device() -> str:
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def linear_to_mulaw(x, mu=255):
    """Convert float PCM (-1..1) to µ-law 8-bit."""
    x = np.clip(x, -1.0, 1.0)
    y = np.sign(x) * np.log(1 + mu * np.abs(x)) / np.log(1 + mu)
    return ((y + 1) * 127.5).astype(np.uint8)


def resample_to_8k(audio_float, orig_sr=24000):
    """Downsample float32 PCM to 8000 Hz."""
    import librosa
    return librosa.resample(audio_float, orig_sr=orig_sr, target_sr=8000)


def chunk_text(text: str, max_words: int = 20) -> list[str]:
    text = text.strip()
    if not text:
        return []

    total_words = len(text.split())
    if total_words <= max_words:
        return [text]

    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        words = sentence.split()
        if len(words) <= max_words:
            chunks.append(sentence)
            continue

        for i in range(0, len(words), max_words):
            chunks.append(" ".join(words[i:i + max_words]))

    return chunks


@app.on_event("startup")
async def _init():
    global pipeline
    device = get_device()
    pipeline = KPipeline(
        lang_code=CONFIG["lang_code"],
        device=device
    )
    logging.info(f"🚀 Kokoro TTS initialized (device={device}, lang={CONFIG['lang_code']})")

@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "Kokoro TTS WebSocket server\n\n"
        "Formats: f32 | s16 | wav | mp3 | ogg | flac | mulaw | pcm8 | s16_8k\n"
    )


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    logging.info("connection opened")

    try:
        while True:
            start = time.time()
            print(f"----------START TIME: {start}------------")

            req = await websocket.receive_text()
            cfg = json.loads(req)

            text = str(cfg.get("text", "")).strip()
            voice = str(cfg.get("voice", CONFIG["voice"]))
            speed = float(cfg.get("speed", CONFIG["speed"]))
            fmt = str(cfg.get("format", CONFIG["format"])).lower()

            if not text:
                await websocket.send_text(json.dumps({"type": "done", "error": "empty text"}))
                continue

            await websocket.send_text(json.dumps({
                "type": "meta",
                "sample_rate": SR,
                "channels": 1,
                "sample_format": fmt
            }))

            # Chunking
            chunks = chunk_text(text, WORD_THRESHOLD) if CHUNK_ENABLED else [text]

            only_pipeline_start = time.time()
            print(f"----------ONLY PIPELINE START TIME: {only_pipeline_start}------------")

            t0 = time.perf_counter()
            ttfa_sent = False
            segments = 0
            audio_total_s = 0.0
            buf: List[np.ndarray] = []

            # Process each chunk
            for chunk in chunks:
                gen = pipeline(chunk, voice=voice, speed=speed,
                               split_pattern=CONFIG["pipeline"]["split_pattern"])

                for (_gs, _ps, audio) in gen:
                    now = time.perf_counter()

                    if not ttfa_sent:
                        await websocket.send_text(json.dumps(
                            {"type": "ttfa", "ms": (now - t0) * 1000.0}
                        ))
                        ttfa_sent = True

                    a = as_numpy(audio)
                    buf.append(a)

                    segments += 1
                    audio_total_s += a.size / SR

                    # Minimal processing + immediate streaming
                    if fmt == "f32":
                        await websocket.send_bytes(a.tobytes())

                    elif fmt == "s16":
                        pcm16 = (np.clip(a, -1, 1) * 32767.0).astype(np.int16)
                        await websocket.send_bytes(pcm16.tobytes())

                    elif fmt in {"mulaw", "pcm8", "s16_8k"}:
                        # Resample to 8k
                        a_8k = resample_to_8k(a, orig_sr=SR)

                        if fmt == "mulaw":
                            encoded = linear_to_mulaw(a_8k)
                            await websocket.send_bytes(encoded.tobytes())

                        elif fmt == "pcm8":
                            await websocket.send_bytes(a_8k.astype(np.float32).tobytes())

                        elif fmt == "s16_8k":
                            pcm16_8k = (np.clip(a_8k, -1, 1) * 32767.0).astype(np.int16)
                            await websocket.send_bytes(pcm16_8k.tobytes())

            print(f"---------------ONLY PIPELINE Time taken: {time.time() - only_pipeline_start} seconds-----------")

            total_ms = (time.perf_counter() - t0) * 1000.0
            rtf = (total_ms / 1000.0) / max(1e-6, audio_total_s)

            # Threaded encoding (mp3, ogg, flac)
            if fmt in {"wav", "mp3", "ogg", "flac"}:
                full_audio = np.concatenate(buf) if len(buf) > 1 else buf[0]

                # Direct WAV creation
                wav_io = BytesIO()
                sf.write(wav_io, np.clip(full_audio, -1, 1), SR,
                         format="WAV", subtype="PCM_16")
                wav_bytes = wav_io.getvalue()

                if fmt == "wav":
                    await websocket.send_bytes(wav_bytes)

                else:
                    loop = asyncio.get_running_loop()

                    def encode_fn():
                        audio_seg = AudioSegment.from_file(BytesIO(wav_bytes), format="wav")
                        out = BytesIO()
                        audio_seg.export(out, format=fmt)
                        return out.getvalue()

                    encoded_bytes = await loop.run_in_executor(executor, encode_fn)
                    await websocket.send_bytes(encoded_bytes)

            # DONE message
            await websocket.send_text(json.dumps({
                "type": "done",
                "total_ms": total_ms,
                "audio_ms": audio_total_s * 1000.0,
                "segments": segments,
                "rtf": rtf,
                "error": None
            }))

            print(f"---------------Time taken: {time.time() - start} seconds-----------")

    except WebSocketDisconnect:
        logging.warning("Client disconnected.")
    except Exception as e:
        logging.error(traceback.format_exc())
        try:
            await websocket.send_text(json.dumps(
                {"type": "done", "error": str(e)}
            ))
        except:
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

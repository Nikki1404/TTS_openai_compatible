import requests
import base64
import struct
import time
import datetime
import re


# ---------------------------------------------------
# Convert audio/L16 (PCM 16-bit) → WAV
# ---------------------------------------------------
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
        1,                       # PCM
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size
    )

    return header + l16_bytes


# ---------------------------------------------------
# Save with unique filename
# ---------------------------------------------------
def generate_filename(voice, text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Clean text preview (only letters & numbers)
    preview = re.sub(r'[^A-Za-z0-9]+', '_', text[:15])

    filename = f"tts_{voice}_{preview}_{timestamp}.wav"
    return filename


# ---------------------------------------------------
# Gemini TTS - Single Speaker Version WITH LATENCY + UNIQUE SAVING
# ---------------------------------------------------
def generate_single_speaker_tts(api_key, text, voice):

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash-preview-tts:generateContent"
        f"?key={api_key}"
    )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": text}]}
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice
                    }
                }
            }
        }
    }

    # ---------- Start timing ----------
    t_start = time.time()
    response = requests.post(url, json=payload)
    t_api = time.time()

    print("\nStatus:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    # Extract audio
    data = response.json()
    inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    audio_b64 = inline["data"]
    mime_type = inline["mimeType"]

    raw_l16 = base64.b64decode(audio_b64)

    sample_rate = 24000
    if "rate=" in mime_type:
        sample_rate = int(mime_type.split("rate=")[1])

    wav_bytes = l16_to_wav(raw_l16, sample_rate)

    # ---------- End timing ----------
    t_end = time.time()

    print("\n====== LATENCY REPORT ======")
    print(f"API Latency:     {(t_api - t_start)*1000:.2f} ms")
    print(f"Total Latency:   {(t_end - t_start)*1000:.2f} ms")
    print("==============================")

    # ---------- Save uniquely ----------
    filename = generate_filename(voice, text)
    with open(filename, "wb") as f:
        f.write(wav_bytes)

    print(f"Saved → {filename}\n")


# ---------------------------------------------------
# INTERACTIVE MODE
# ---------------------------------------------------
if __name__ == "__main__":
    API_KEY = "YOUR_REAL_GEMINI_API_KEY_HERE"

    print("=== Gemini TTS Interactive Mode ===")
    print("Voices: Kore, Leda, Aoede, Fenrir, Charon, Wraith")
    print("Outputs will be saved as SEPARATE .wav files")
    print("Type 'exit' anytime to quit.")
    print("----------------------------------------")

    while True:
        text = input("\nEnter text: ").strip()
        if text.lower() == "exit":
            break

        voice = input("Choose voice (default Kore): ").strip()
        if voice == "":
            voice = "Kore"

        generate_single_speaker_tts(API_KEY, text, voice)

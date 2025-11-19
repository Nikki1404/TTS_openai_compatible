import requests
import base64
import struct


# ---------------------------------------------------
# Convert audio/L16 (PCM 16-bit) → WAV
# (Python port of convertL16ToWav_() from your JS code)
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
# Gemini TTS - Single Speaker Version
# ---------------------------------------------------
def generate_single_speaker_tts(api_key, text):
    # 🟢 Your actual Gemini endpoint
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash-preview-tts:generateContent"
        f"?key={api_key}"
    )

    # 🟢 Payload (single speaker)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": text}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Kore"   # ⭐ choose voice here
                    }
                }
            }
        }
    }

    response = requests.post(url, json=payload)
    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    data = response.json()

    # Extract inline audio
    inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
    audio_b64 = inline["data"]
    mime_type = inline["mimeType"]  # e.g., "audio/L16;rate=24000"

    raw_l16 = base64.b64decode(audio_b64)

    # Extract sample rate
    sample_rate = 24000
    if "rate=" in mime_type:
        sample_rate = int(mime_type.split("rate=")[1])

    # Convert raw PCM → WAV
    wav_bytes = l16_to_wav(raw_l16, sample_rate=sample_rate)

    # Save WAV file
    with open("single_speaker.wav", "wb") as f:
        f.write(wav_bytes)

    print("Saved → single_speaker.wav")


if __name__ == "__main__":
    # 🔥 THIS IS WHERE YOU PASS YOUR GEMINI API KEY
    API_KEY = "YOUR_REAL_GEMINI_API_KEY_HERE"

    text = "Hello! This is a test of Gemini single speaker text to speech."
    generate_single_speaker_tts(API_KEY, text)

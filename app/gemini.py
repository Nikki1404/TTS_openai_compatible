import requests
import base64
import struct
import time

# ---------------------------------------------------
# Pre-compiled struct for WAV header (faster)
# ---------------------------------------------------
WAV_HEADER_STRUCT = struct.Struct("<4sI4s4sIHHIIHH4sI")

def l16_to_wav_fast(l16_bytes: bytes, sample_rate=24000, num_channels=1):
    bits_per_sample = 16
    block_align = num_channels * bits_per_sample // 8
    byte_rate = sample_rate * block_align
    data_size = len(l16_bytes)
    riff_size = 36 + data_size

    header = WAV_HEADER_STRUCT.pack(
        b"RIFF",
        riff_size,
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


# ---------------------------------------------------
# Gemini TTS optimized latency tester
# ---------------------------------------------------
def create_payload(text, voice="Kore"):
    return {
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


# ---------------------------------------------------
# Main TTS function with persistent HTTP session
# ---------------------------------------------------
def tts_low_latency(api_key, text, session, url):
    payload = create_payload(text)

    t_start = time.time()
    response = session.post(url, json=payload)
    t_api = time.time()

    if response.status_code != 200:
        print("Error:", response.text)
        return

    inline = response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]

    # Decode L16 PCM audio
    raw_l16 = base64.b64decode(inline["data"])

    sample_rate = 24000
    if "rate=" in inline["mimeType"]:
        sample_rate = int(inline["mimeType"].split("rate=")[1])

    # Convert to WAV efficiently
    wav_bytes = l16_to_wav_fast(raw_l16, sample_rate)

    t_end = time.time()

    # Save (fast I/O buffered write)
    with open("output.wav", "wb", buffering=65536) as f:
        f.write(wav_bytes)

    print("\n====== LOW LATENCY REPORT ======")
    print(f"API Time:            {(t_api - t_start)*1000:.2f} ms")
    print(f"Processing Time:     {(t_end - t_api)*1000:.2f} ms")
    print(f"TOTAL Time:          {(t_end - t_start)*1000:.2f} ms")
    print("Saved → output.wav\n")


# ---------------------------------------------------
# Interactive Loop
# ---------------------------------------------------
if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY_HERE"

    session = requests.Session()  # Persistent connection = big speed win

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.0-flash-lite-preview-tts:generateContent"
        f"?key={API_KEY}"
    )

    print("Gemini Low Latency TTS Tester (type 'exit' to quit)\n")

    while True:
        text = input("Enter text: ").strip()
        if text.lower() == "exit":
            break
        tts_low_latency(API_KEY, text, session, url)

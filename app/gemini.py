import requests
import base64
import struct
import time
import datetime
import re


# ---------------------------------------------------
# Convert audio/L16 PCM → WAV
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
# Convert L16 → MULAW (8-bit companded)
# ---------------------------------------------------
def l16_to_mulaw(l16_bytes):
    mulaw_bytes = bytearray()
    for i in range(0, len(l16_bytes), 2):
        sample = struct.unpack("<h", l16_bytes[i:i+2])[0]
        mulaw_bytes.append(linear2ulaw(sample))
    return bytes(mulaw_bytes)


# μ-law conversion (G.711)
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


# ---------------------------------------------------
# Unique filename generator
# ---------------------------------------------------
def generate_filename(prefix, voice, text, ext):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    preview = re.sub(r'[^A-Za-z0-9]+', '_', text[:12])
    return f"{prefix}_{voice}_{preview}_{timestamp}.{ext}"


# ---------------------------------------------------
# Gemini TTS: WAV + MULAW + LATENCY
# ---------------------------------------------------
def generate_tts(api_key, text, voice):
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
                    "prebuiltVoiceConfig": {"voiceName": voice}
                }
            }
        }
    }

    # ----------- Start Latency -----------
    t_start = time.time()
    response = requests.post(url, json=payload)
    t_api = time.time()

    if response.status_code != 200:
        print(response.text)
        return

    data = response.json()
    inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]

    raw_l16 = base64.b64decode(inline["data"])

    # Extract sample rate
    mime = inline["mimeType"]
    sample_rate = 24000
    if "rate=" in mime:
        sample_rate = int(mime.split("rate=")[1])

    # ----------- WAV ENCODE -----------
    t_wav_start = time.time()
    wav_data = l16_to_wav(raw_l16, sample_rate)
    t_wav_end = time.time()

    wav_file = generate_filename("tts_wav", voice, text, "wav")
    with open(wav_file, "wb") as f:
        f.write(wav_data)

    # ----------- MULAW ENCODE -----------
    t_mulaw_start = time.time()
    mulaw_data = l16_to_mulaw(raw_l16)
    t_mulaw_end = time.time()

    mulaw_file = generate_filename("tts_mulaw", voice, text, "mulaw")
    with open(mulaw_file, "wb") as f:
        f.write(mulaw_data)

    t_end = time.time()

    # ----------- LATENCY REPORT -----------
    print("\n====== LATENCY REPORT ======")
    print(f"API Latency:            {(t_api - t_start)*1000:.2f} ms")
    print(f"WAV Encode Latency:     {(t_wav_end - t_wav_start)*1000:.2f} ms")
    print(f"MULAW Encode Latency:   {(t_mulaw_end - t_mulaw_start)*1000:.2f} ms")
    print(f"TOTAL Time:             {(t_end - t_start)*1000:.2f} ms")
    print("==============================")

    print(f"Saved WAV  → {wav_file}")
    print(f"Saved MULAW → {mulaw_file}\n")


# ---------------------------------------------------
# INTERACTIVE MODE
# ---------------------------------------------------
if __name__ == "__main__":
    API_KEY = "YOUR_REAL_GEMINI_API_KEY_HERE"

    print("=== Gemini TTS (WAV + MULAW) ===")
    print("Voices: Kore, Leda, Aoede, Fenrir, Charon, Wraith")
    print("Type text and press Enter. Type 'exit' to quit.\n")

    while True:
        text = input("Enter text: ").strip()
        if text.lower() == "exit":
            break

        voice = input("Choose voice (default Kore): ").strip()
        if voice == "":
            voice = "Kore"

        generate_tts(API_KEY, text, voice)

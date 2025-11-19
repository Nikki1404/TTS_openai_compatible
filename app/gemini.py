import requests
import base64
import struct
import time
import datetime
import re


# ---------------------------------------------------
# Convert audio/L16 → WAV
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
        1,                 
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
# Convert L16 → MULAW bytes
# ---------------------------------------------------
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
    return ~(sign | (exponent << 4) | mantissa) & 0xFF


def l16_to_mulaw(l16_bytes):
    out = bytearray()
    for i in range(0, len(l16_bytes), 2):
        sample = struct.unpack("<h", l16_bytes[i:i+2])[0]
        out.append(linear2ulaw(sample))
    return bytes(out)


# ---------------------------------------------------
# Unique file naming
# ---------------------------------------------------
def make_filename(prefix, voice, text, ext):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    short = re.sub(r'[^A-Za-z0-9]+', '_', text[:12])
    return f"{prefix}_{voice}_{short}_{timestamp}.{ext}"


# ---------------------------------------------------
# Gemini TTS with FULL TIMING
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

    # -------------------------------------------------------
    # TOTAL START TIME
    # -------------------------------------------------------
    total_start = time.time()

    # -------------------------------------------------------
    # API CALL TIMING
    # -------------------------------------------------------
    api_start = time.time()
    response = requests.post(url, json=payload)
    api_end = time.time()

    if response.status_code != 200:
        print(response.text)
        return

    data = response.json()
    inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]

    l16_raw = base64.b64decode(inline["data"])

    sample_rate = 24000
    if "rate=" in inline["mimeType"]:
        sample_rate = int(inline["mimeType"].split("rate=")[1])

    # -------------------------------------------------------
    # WAV GENERATION TIMING
    # -------------------------------------------------------
    wav_start = time.time()
    wav_bytes = l16_to_wav(l16_raw, sample_rate)
    wav_end = time.time()

    wav_file = make_filename("tts_wav", voice, text, "wav")
    with open(wav_file, "wb") as f:
        f.write(wav_bytes)

    # -------------------------------------------------------
    # MULAW GENERATION TIMING
    # -------------------------------------------------------
    mulaw_start = time.time()
    mulaw_bytes = l16_to_mulaw(l16_raw)
    mulaw_end = time.time()

    mulaw_file = make_filename("tts_mulaw", voice, text, "mulaw")
    with open(mulaw_file, "wb") as f:
        f.write(mulaw_bytes)

    # -------------------------------------------------------
    # TOTAL END TIME
    # -------------------------------------------------------
    total_end = time.time()

    # -------------------------------------------------------
    # LATENCY REPORT
    # -------------------------------------------------------
    print("\n================ LATENCY REPORT ================")
    print(f"API Start Time:    {api_start}")
    print(f"API End Time:      {api_end}")
    print(f"API Latency:       {(api_end - api_start)*1000:.2f} ms\n")

    print(f"WAV Start Time:    {wav_start}")
    print(f"WAV End Time:      {wav_end}")
    print(f"WAV Latency:       {(wav_end - wav_start)*1000:.2f} ms\n")

    print(f"MULAW Start Time:  {mulaw_start}")
    print(f"MULAW End Time:    {mulaw_end}")
    print(f"MULAW Latency:     {(mulaw_end - mulaw_start)*1000:.2f} ms\n")

    print(f"TOTAL Start Time:  {total_start}")
    print(f"TOTAL End Time:    {total_end}")
    print(f"TOTAL Latency:     {(total_end - total_start)*1000:.2f} ms")
    print("=================================================\n")

    print(f"Saved WAV   → {wav_file}")
    print(f"Saved MULAW → {mulaw_file}\n")


# ---------------------------------------------------
# INTERACTIVE MODE
# ---------------------------------------------------
if __name__ == "__main__":
    API_KEY = "YOUR_REAL_GEMINI_API_KEY_HERE"

    print("=== Gemini TTS (WAV + MULAW) with FULL TIMESTAMPS ===")

    while True:
        text = input("\nEnter text (or 'exit'): ").strip()
        if text.lower() == "exit":
            break

        voice = input("Choose voice (default Kore): ").strip()
        if voice == "":
            voice = "Kore"

        generate_tts(API_KEY, text, voice)

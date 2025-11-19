import time
import base64
from google import generativeai as genai

# -------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------
API_KEY = "YOUR_API_KEY"  # Or use environment variable
MODEL_NAME = "gemini-1.5-flash-tts"

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(MODEL_NAME)


def tts_and_measure(text: str):
    print("\n====== GEMINI TTS LATENCY TEST ======")
    print(f"Input Text: {text}")
    print("------------------------------------")

    # Start timer
    t_start = time.time()

    response = model.generate_content(
        text,
        generation_config={
            "audio_format": "wav",
            "voice": "Female"      # You can choose: Male / Female / Neutral
        }
    )

    t_after_api = time.time()

    # ----------------------------------------------------------------
    # Extract audio bytes (Gemini returns base64-encoded audio content)
    # ----------------------------------------------------------------
    audio_base64 = response.candidates[0].content.parts[0].data
    audio_bytes = base64.b64decode(audio_base64)

    t_after_decode = time.time()

    # ---------------------------------------------------------------
    # Print Latency Breakdown
    # ---------------------------------------------------------------
    print(f"API Response Time:        {(t_after_api - t_start)*1000:.2f} ms")
    print(f"Audio Decode Time:        {(t_after_decode - t_after_api)*1000:.2f} ms")
    print(f"Total Time:               {(t_after_decode - t_start)*1000:.2f} ms")
    print(f"Audio Output Size (KB):   {len(audio_bytes)/1024:.2f} KB")

    # Save file
    out_file = "output.wav"
    with open(out_file, "wb") as f:
        f.write(audio_bytes)

    print(f"\nSaved audio to {out_file}")
    print("====================================\n")


if __name__ == "__main__":
    while True:
        text = input("Enter text (or 'exit'): ").strip()
        if text.lower() == "exit":
            break
        tts_and_measure(text)

import time
import base64
from google import generativeai as genai

API_KEY = "YOUR_API_KEY"   # or use environment variable

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-1.5-pro-tts")


def tts_and_measure(text: str):
    print("\n====== GEMINI TTS LATENCY TEST ======")
    print(f"Input Text: {text}")
    print("------------------------------------")

    t_start = time.time()

    # TTS call
    response = model.generate_audio(
        text=text,
        voice="FEMALE_1",  # Options: FEMALE_1, FEMALE_2, MALE_1, MALE_2
        encoding="wav"      # wav / mp3
    )

    t_after_api = time.time()

    # Extract audio
    audio_bytes = base64.b64decode(response.audio.data)

    t_after_decode = time.time()

    # Latency breakdown
    print(f"API Response Time:        {(t_after_api - t_start)*1000:.2f} ms")
    print(f"Audio Decode Time:        {(t_after_decode - t_after_api)*1000:.2f} ms")
    print(f"Total Time:               {(t_after_decode - t_start)*1000:.2f} ms")
    print(f"Audio Output Size (KB):   {len(audio_bytes)/1024:.2f} KB")

    # Save audio
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    print("\nSaved as output.wav")
    print("====================================\n")


if __name__ == "__main__":
    while True:
        text = input("Enter text (or 'exit'): ")
        if text.lower() == "exit":
            break
        tts_and_measure(text)

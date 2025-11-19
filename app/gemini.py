import time
import requests
import base64
import json

API_KEY = "YOUR_API_KEY"
MODEL = "models/gemini-1.5-flash"     # TTS-enabled model

def tts_and_measure(text: str):
    print("\n====== GEMINI TTS LATENCY (REST API) ======")
    print(f"Input Text: {text}")
    print("------------------------------------------")

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": text
            }]
        }],
        "generationConfig": {
            "response_mime_type": "audio/wav"   # or audio/mp3
        }
    }

    t_start = time.time()
    response = requests.post(url, json=payload)
    t_api = time.time()

    data = response.json()

    # extract audio base64
    audio_base64 = data["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
    audio_bytes = base64.b64decode(audio_base64)

    t_decode = time.time()

    # Latency summary
    print(f"API Response Time:        {(t_api - t_start)*1000:.2f} ms")
    print(f"Audio Decode Time:        {(t_decode - t_api)*1000:.2f} ms")
    print(f"Total Time:               {(t_decode - t_start)*1000:.2f} ms")
    print(f"Audio Output Size (KB):   {len(audio_bytes)/1024:.2f}")

    # Write wav file
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    print("\nSaved audio to output.wav")
    print("==========================================\n")


if __name__ == "__main__":
    while True:
        text = input("Enter text (or 'exit'): ")
        if text.lower() == "exit":
            break
        tts_and_measure(text)

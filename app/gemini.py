import time
import requests
import base64

API_KEY = "YOUR_API_KEY"
MODEL = "models/gemini-1.5-tts"   # IMPORTANT: Actual TTS model

def tts_and_measure(text: str):
    print("\n====== GEMINI TTS LATENCY ======")
    print(f"Input: {text}")
    print("--------------------------------")

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateAudio?key={API_KEY}"

    payload = {
        "text": text,
        "audioConfig": {
            "audioEncoding": "LINEAR16"   # produces WAV PCM16
        }
    }

    t_start = time.time()
    response = requests.post(url, json=payload)
    t_api = time.time()

    if response.status_code != 200:
        print("❌ API Error:", response.text)
        return

    data = response.json()

    # Extract audio
    audio_b64 = data["audioContent"]
    audio_bytes = base64.b64decode(audio_b64)

    t_decode = time.time()

    print(f"API Response Time:  {(t_api - t_start)*1000:.2f} ms")
    print(f"Decode Time:        {(t_decode - t_api)*1000:.2f} ms")
    print(f"Total Time:         {(t_decode - t_start)*1000:.2f} ms")
    print(f"Audio Size:         {len(audio_bytes)/1024:.2f} KB")

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)

    print("Saved: output.wav\n")


if __name__ == "__main__":
    while True:
        text = input("Enter text (or 'exit'): ").strip()
        if text.lower() == "exit":
            break
        tts_and_measure(text)

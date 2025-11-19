import os
import time
import google.generativeai as genai
from packaging import version
import numpy as np
import sounddevice as sd
import soundfile as sf


GENAI_VERSION = version.parse(genai.__version__)
print("Using google-generativeai =", GENAI_VERSION)


class GeminiTelephonyTTS:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-tts-1")

    def now_us(self):
        return time.perf_counter_ns() / 1000

    def synthesize_interactive(self):
        print("\n===== Gemini TTS Interactive Mode =====")
        print("Type text to synthesize. Type 'exit' to quit.\n")

        while True:
            text = input("You: ").strip()
            if text.lower() == "exit":
                break
            if text:
                self.generate_and_play(text)

    # μ-law encoding
    def pcm16_to_mulaw(self, pcm16):
        mu = 255
        pcm = pcm16.astype(np.float32) / 32768.0
        pcm = np.sign(pcm) * np.log1p(mu * np.abs(pcm)) / np.log1p(mu)
        return ((pcm + 1) * 127.5).astype(np.uint8)

    # μ-law decoding
    def mulaw_to_pcm16(self, mulaw):
        mu = 255
        x = mulaw.astype(np.float32) / 127.5 - 1
        pcm = np.sign(x) * ((1 + mu) ** np.abs(x) - 1) / mu
        return (pcm * 32767).astype(np.int16)

    def generate_and_play(self, text):

        # Detect API change
        new_api = GENAI_VERSION >= version.parse("0.7.0")

        print("\nGenerating with", ("NEW API" if new_api else "OLD API"), "...\n")

        api_start = self.now_us()

        if new_api:
            # ✔ NEW GEMINI TTS API
            response = self.model.generate_content(
                text,
                generation_config={
                    "response_mime_type": "audio/wav",
                    "voice_config": {"voice_name": "Pine"},
                }
            )
        else:
            # ✔ FALLBACK for older SDKs
            response = self.model.generate_content(
                {
                    "text": text,
                    "audio": {
                        "voice": "Pine",
                        "format": "wav",
                    }
                }
            )

        api_first = self.now_us()
        wav_bytes = response.candidates[0].content[0].binary
        api_end = self.now_us()

        print("TTFB:", (api_first - api_start)/1000, "ms")
        print("Total WAV latency:", (api_end - api_start)/1000, "ms")

        # Save WAV
        with open("gemini.wav", "wb") as f:
            f.write(wav_bytes)

        # Play WAV
        data, sr = sf.read("gemini.wav")
        sd.play(data, sr)
        sd.wait()

        # MULAW conversion
        conv_start = self.now_us()
        pcm16 = (data * 32767).astype(np.int16)
        mulaw = self.pcm16_to_mulaw(pcm16)
        conv_end = self.now_us()

        print("MULAW conversion latency:", (conv_end - conv_start)/1000, "ms")

        # Play MULAW
        pcm16_dec = self.mulaw_to_pcm16(mulaw)
        sd.play(pcm16_dec.astype(np.float32) / 32767.0, 8000)
        sd.wait()

        print("MULAW played.\n")


if __name__ == "__main__":
    tts = GeminiTelephonyTTS()
    tts.synthesize_interactive()

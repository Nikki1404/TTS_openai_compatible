import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import google.generativeai as genai


class GeminiTTSLatency:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-tts-1")

    def now_us(self):
        return time.perf_counter_ns() / 1000

    def pcm16_to_mulaw(self, pcm16):
        MU = 255
        pcm = pcm16.astype(np.float32) / 32768.0
        mulaw = np.sign(pcm) * np.log1p(MU * np.abs(pcm)) / np.log1p(MU)
        return ((mulaw + 1) * 127.5).astype(np.uint8)

    def mulaw_to_pcm16(self, mulaw):
        MU = 255
        x = mulaw.astype(np.float32) / 127.5 - 1
        pcm = np.sign(x) * ((1 + MU) ** np.abs(x) - 1) / MU
        return (pcm * 32767).astype(np.int16)

    def generate_and_measure(self, text):

        print("\n====== GEMINI TTS LATENCY REPORT ======\n")
        print(f"Text: {text}")
        print("-------------------------------------")

        # CORRECT API FORMAT FOR SDK 0.8.5
        generation_config = {
            "response_mime_type": "audio/wav",
            "audio": {
                "voice_name": "Pine",
                "audio_encoding": "LINEAR16"   # WAV PCM
            }
        }

        # ---------------- API Call Timing ----------------
        api_start = self.now_us()

        response = self.model.generate_content(
            text,
            generation_config=generation_config
        )

        api_first = self.now_us()
        wav_bytes = response.candidates[0].content[0].binary
        api_end = self.now_us()

        print(f"TTFB (first byte):          {(api_first - api_start)/1000:.2f} ms")
        print(f"Total API latency:          {(api_end - api_start)/1000:.2f} ms")
        print(f"WAV Size:                   {len(wav_bytes)} bytes\n")

        # Save WAV
        with open("gemini.wav", "wb") as f:
            f.write(wav_bytes)

        # WAV PLAY
        wav_data, wav_sr = sf.read("gemini.wav")
        print("Playing WAV...")
        wav_play_start = self.now_us()
        sd.play(wav_data, wav_sr)
        sd.wait()
        wav_play_end = self.now_us()
        print(f"WAV Playback Latency:       {(wav_play_end - wav_play_start)/1000:.2f} ms\n")

        # MULAW CONVERSION
        pcm16 = (wav_data * 32767).astype(np.int16)
        conv_start = self.now_us()
        mulaw = self.pcm16_to_mulaw(pcm16)
        conv_end = self.now_us()

        print(f"MULAW Conversion Latency:   {(conv_end - conv_start)/1000:.2f} ms")
        print(f"MULAW Size:                 {len(mulaw)} bytes\n")

        # MULAW PLAYBACK
        pcm16_decoded = self.mulaw_to_pcm16(mulaw).astype(np.float32) / 32767.0
        print("Playing MULAW (8kHz)...")
        mulaw_play_start = self.now_us()
        sd.play(pcm16_decoded, 8000)
        sd.wait()
        mulaw_play_end = self.now_us()

        print(f"MULAW Playback Latency:     {(mulaw_play_end - mulaw_play_start)/1000:.2f} ms\n")

        print("Saved files:")
        print(" - gemini.wav")
        print(" - gemini_output_mulaw.raw")

        with open("gemini_output_mulaw.raw", "wb") as f:
            f.write(mulaw.tobytes())

        print("============== END REPORT ==============\n")


if __name__ == "__main__":
    tts = GeminiTTSLatency()
    while True:
        text = input("Enter text (or 'exit'): ").strip()
        if text.lower() == "exit":
            break
        tts.generate_and_measure(text)

import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import google.generativeai as genai


class GeminiTelephonyTTS:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-tts-1")

    @staticmethod
    def now_us():
        return time.perf_counter_ns() / 1000  # microseconds

    def synthesize_interactive(self):
        print("\n===== Gemini TTS Interactive Telephony Mode =====")
        print("Type something to synthesize. Type 'exit' to quit.\n")

        while True:
            text = input("You: ").strip()
            if text.lower() in ["exit", "quit"]:
                print("Exiting...")
                break

            if text:
                self.generate_and_play(text)

    def generate_and_play(self, text):
        # -----------------------------------------
        # 1) Gemini TTS → WAV (measure latency)
        # -----------------------------------------
        api_start = self.now_us()

        response = self.model.generate_content(
            text,
            generation_config={
                "response_mime_type": "audio/wav",
                "voice_config": {"voice_name": "Pine"},
            }
        )

        api_first_byte = self.now_us()

        wav_bytes = response.candidates[0].content[0].binary
        api_end = self.now_us()

        ttfb_us = api_first_byte - api_start
        wav_latency_us = api_end - api_start

        print("\n========== WAV LATENCY ==========")
        print(f"TTFB:                      {ttfb_us/1000:.2f} ms")
        print(f"Full WAV Latency:          {wav_latency_us/1000:.2f} ms")
        print(f"WAV Size:                  {len(wav_bytes)} bytes")

        # Save WAV
        wav_path = "gemini_output.wav"
        with open(wav_path, "wb") as f:
            f.write(wav_bytes)

        # -----------------------------------------
        # Play WAV using soundfile + sounddevice
        # -----------------------------------------
        data, samplerate = sf.read(wav_path)
        print("Playing WAV...")
        sd.play(data, samplerate)
        sd.wait()

        # -----------------------------------------
        # 2) Convert WAV → MULAW manually
        # -----------------------------------------
        mulaw_conv_start = self.now_us()

        # Convert PCM16 → MULAW
        pcm16 = (data * 32767).astype(np.int16)
        mulaw_encoded = self.pcm16_to_mulaw(pcm16).astype(np.uint8)
        mulaw_raw = mulaw_encoded.tobytes()

        mulaw_conv_end = self.now_us()

        print("\n========== MULAW LATENCY ==========")
        print(f"MULAW Conversion Latency:   {(mulaw_conv_end - mulaw_conv_start)/1000:.2f} ms")
        print(f"MULAW Size:                 {len(mulaw_raw)} bytes")

        # Save raw mulaw
        mulaw_path = "gemini_output_mulaw.raw"
        with open(mulaw_path, "wb") as f:
            f.write(mulaw_raw)

        # -----------------------------------------
        # PLAY MULAW (convert back → PCM16 → play)
        # -----------------------------------------
        print("Playing MULAW (Telephony 8 kHz)...")

        mulaw_play_start = self.now_us()

        pcm16_decoded = self.mulaw_to_pcm16(mulaw_encoded)
        sd.play(pcm16_decoded.astype(np.float32) / 32767.0, 8000)
        sd.wait()

        mulaw_play_end = self.now_us()

        print(f"MULAW Playback Latency:     {(mulaw_play_end - mulaw_play_start)/1000:.2f} ms\n")

        print("Saved files:")
        print(f" - {wav_path}")
        print(f" - {mulaw_path}")
        print("----------------------------------------------\n")

    # μ-law encoding
    def pcm16_to_mulaw(self, pcm16):
        MU = 255
        max_val = np.max(np.abs(pcm16))
        pcm = pcm16.astype(np.float32) / (max_val + 1)
        pcm = np.sign(pcm) * np.log1p(MU * np.abs(pcm)) / np.log1p(MU)
        return ((pcm + 1) * 127.5).astype(np.uint8)

    # μ-law decoding
    def mulaw_to_pcm16(self, mulaw):
        MU = 255
        mulaw = mulaw.astype(np.float32)
        pcm = (mulaw / 127.5) - 1
        pcm = np.sign(pcm) * ((1 + MU) ** np.abs(pcm) - 1) / MU
        return (pcm * 32767).astype(np.int16)


if __name__ == "__main__":
    tts = GeminiTelephonyTTS()
    tts.synthesize_interactive()

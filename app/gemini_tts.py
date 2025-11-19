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
            raise RuntimeError("GEMINI_API_KEY is not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-tts-1")

    @staticmethod
    def now_us():
        """High precision microsecond timer."""
        return time.perf_counter_ns() / 1000

    def pcm16_to_mulaw(self, pcm16):
        """Encode PCM16 → μ-law."""
        MU = 255
        pcm = pcm16.astype(np.float32) / 32768.0
        mulaw = np.sign(pcm) * np.log1p(MU * np.abs(pcm)) / np.log1p(MU)
        return ((mulaw + 1) * 127.5).astype(np.uint8)

    def mulaw_to_pcm16(self, mulaw):
        """Decode μ-law → PCM16."""
        MU = 255
        x = mulaw.astype(np.float32) / 127.5 - 1
        pcm = np.sign(x) * ((1 + MU) ** np.abs(x) - 1) / MU
        return (pcm * 32767).astype(np.int16)

    def generate_and_measure(self, text):

        print("\n====== GEMINI TTS FULL LATENCY REPORT ======\n")
        print("Input Text:", text)
        print("--------------------------------------------")

        # ---------------------------------------------------
        # 1) GEMINI TTS API CALL LATENCY (TTFB + TOTAL)
        # ---------------------------------------------------
        api_start = self.now_us()

        response = self.model.generate_content(
            text,
            generation_config={
                "response_mime_type": "audio/wav",
                "voice_config": {"voice_name": "Pine"}
            }
        )

        api_first_byte = self.now_us()     # TTFB (first chunk received)

        wav_bytes = response.candidates[0].content[0].binary

        api_end = self.now_us()            # Full response finished

        # Latency Calculations
        ttfb_us = api_first_byte - api_start
        total_api_us = api_end - api_start

        print(f"TTFB (Time to First Byte):   {ttfb_us/1000:.2f} ms")
        print(f"API Total Latency (WAV):     {total_api_us/1000:.2f} ms")
        print(f"WAV Bytes Received:          {len(wav_bytes)} bytes\n")

        # ---------------------------------------------------
        # 2) WAV Saving + Playback Latency
        # ---------------------------------------------------
        with open("gemini.wav", "wb") as f:
            f.write(wav_bytes)

        wav_data, wav_sr = sf.read("gemini.wav")

        print("Playing WAV...")
        wav_play_start = self.now_us()
        sd.play(wav_data, wav_sr)
        sd.wait()
        wav_play_end = self.now_us()

        print(f"WAV Playback Latency:        {(wav_play_end - wav_play_start)/1000:.2f} ms\n")

        # ---------------------------------------------------
        # 3) WAV → MULAW Conversion Latency
        # ---------------------------------------------------
        conv_start = self.now_us()

        pcm16 = (wav_data * 32767).astype(np.int16)
        mulaw = self.pcm16_to_mulaw(pcm16)

        conv_end = self.now_us()

        mulaw_us = conv_end - conv_start

        print(f"MULAW Conversion Latency:    {mulaw_us/1000:.2f} ms")
        print(f"MULAW Size:                  {len(mulaw)} bytes\n")

        # ---------------------------------------------------
        # 4) MULAW Playback Latency
        # ---------------------------------------------------
        pcm16_decoded = self.mulaw_to_pcm16(mulaw).astype(np.float32) / 32767.0

        print("Playing MULAW (8 kHz telephony)...")
        mulaw_play_start = self.now_us()
        sd.play(pcm16_decoded, 8000)
        sd.wait()
        mulaw_play_end = self.now_us()

        print(f"MULAW Playback Latency:      {(mulaw_play_end - mulaw_play_start)/1000:.2f} ms")

        print("\nSaved:")
        print(" - gemini.wav")
        print(" - gemini_output_mulaw.raw\n")

        # Save raw μ-law
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

(env) PS C:\Users\re_nikitav\tts> python .\gemini-tts.py      
Traceback (most recent call last):
  File "C:\Users\re_nikitav\tts\gemini-tts.py", line 4, in <module>
    from packaging import version
ModuleNotFoundError: No module named 'packaging'
(env) PS C:\Users\re_nikitav\tts> python .\gemini-tts.py
Enter text (or 'exit'): hi

====== GEMINI TTS FULL LATENCY REPORT ======

Input Text: hi
--------------------------------------------
Traceback (most recent call last):
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\marshal\rules\message.py", line 36, in to_proto
    return self._descriptor(**value)
           ~~~~~~~~~~~~~~~~^^^^^^^^^
ValueError: Protocol message GenerationConfig has no "voice_config" field.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\re_nikitav\tts\gemini-tts.py", line 131, in <module>
    tts.generate_and_measure(text)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\re_nikitav\tts\gemini-tts.py", line 48, in generate_and_measure
    response = self.model.generate_content(
        text,
    ...<3 lines>...
        }
    )
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\google\generativeai\generative_models.py", line 305, in generate_content
    request = self._prepare_request(
        contents=contents,
    ...<3 lines>...
        tool_config=tool_config,
    )
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\google\generativeai\generative_models.py", line 165, in _prepare_request
    return protos.GenerateContentRequest(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        model=self._model_name,
        ^^^^^^^^^^^^^^^^^^^^^^^
    ...<6 lines>...
        cached_content=self.cached_content,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\message.py", line 728, in __init__ 
    pb_value = marshal.to_proto(pb_type, value)
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\marshal\marshal.py", line 235, in to_proto
    pb_value = self.get_rule(proto_type=proto_type).to_proto(value)
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\marshal\rules\message.py", line 46, in to_proto
    return self._wrapper(value)._pb
           ~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\message.py", line 724, in __init__ 
    raise ValueError(
        "Unknown field for {}: {}".format(self.__class__.__name__, key)
    )
ValueError: Unknown field for GenerationConfig: voice_config

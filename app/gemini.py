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

(env) PS C:\Users\re_nikitav\tts> python .\gemini-tts.py                                       
Enter text (or 'exit'): hi

====== GEMINI TTS LATENCY TEST ======
Input Text: hi
------------------------------------
Traceback (most recent call last):
  File "C:\Users\re_nikitav\tts\env\Lib\site-packages\proto\marshal\rules\message.py", line 36, in to_proto
    return self._descriptor(**value)
           ~~~~~~~~~~~~~~~~^^^^^^^^^
ValueError: Protocol message GenerationConfig has no "audio_format" field.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\re_nikitav\tts\gemini-tts.py", line 64, in <module>
    tts_and_measure(text)
    ~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\re_nikitav\tts\gemini-tts.py", line 24, in tts_and_measure
    response = model.generate_content(
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
ValueError: Unknown field for GenerationConfig: audio_format
(env) PS C:\Users\re_nikitav\tts> 

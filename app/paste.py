https://huggingface.co/nvidia/parakeet_realtime_eou_120m-v1


==========
== CUDA ==
==========

CUDA Version 12.1.1

Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.

Traceback (most recent call last):
  File "/app/ws_kokoro_server.py", line 31, in <module>
    CONFIG = yaml.safe_load(f)
  File "/usr/local/lib/python3.10/dist-packages/yaml/__init__.py", line 125, in safe_load
    return load(stream, SafeLoader)
  File "/usr/local/lib/python3.10/dist-packages/yaml/__init__.py", line 81, in load
    return loader.get_single_data()
  File "/usr/local/lib/python3.10/dist-packages/yaml/constructor.py", line 49, in get_single_data
    node = self.get_single_node()
  File "/usr/local/lib/python3.10/dist-packages/yaml/composer.py", line 39, in get_single_node
    if not self.check_event(StreamEndEvent):
  File "/usr/local/lib/python3.10/dist-packages/yaml/parser.py", line 98, in check_event
    self.current_event = self.state()
  File "/usr/local/lib/python3.10/dist-packages/yaml/parser.py", line 171, in parse_document_start
    raise ParserError(None, None,
yaml.parser.ParserError: expected '<document start>', but found '<block mapping start>'
  in "config.yaml", line 4, column 1
 

  this is config.yml-

fastapi==0.110.0
nemo_toolkit[asr]>=2.5.0
numpy==1.26.4
pydantic==2.6.3
sounddevice==0.4.6
soundfile==0.12.1
torch==2.3.0
uvicorn==0.29.0
websockets==12.0



benchmark.py-

import os
import time
import json
import numpy as np
import soundfile as sf
import nemo.collections.asr as nemo_asr
import psutil
import subprocess

MODEL_NAME = "nvidia/parakeet_realtime_eou_120m-v1"
TEST_FILES = ["sample1.wav", "sample2.wav"]  # Add your test WAV files here


def gpu_memory():
    """Returns GPU VRAM usage using nvidia-smi."""
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
        )
        return int(result.decode().strip())
    except:
        return -1


def measure_latency(model, wav_path):
    """Measure ASR latency for a single file."""
    start = time.time()
    out = model.transcribe([wav_path])
    latency = time.time() - start
    text = out[0].text
    return latency, text


def word_count(text):
    return len(text.split())


def benchmark():
    print(" Loading model...")
    model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL_NAME)
    print(" Model loaded.\n")

    results = []

    for wav in TEST_FILES:
        print(f"🎧 Testing file: {wav}")

        audio, sr = sf.read(wav)
        if sr != 16000:
            print(" Resampling required for:", wav)

        cpu_before = psutil.cpu_percent()
        mem_before = psutil.virtual_memory().percent
        gpu_before = gpu_memory()

        latency, text = measure_latency(model, wav)

        cpu_after = psutil.cpu_percent()
        mem_after = psutil.virtual_memory().percent
        gpu_after = gpu_memory()

        wc = word_count(text)
        throughput = wc / latency if latency > 0 else 0

        result = {
            "file": wav,
            "latency_sec": latency,
            "words": wc,
            "throughput_wps": throughput,
            "cpu_start": cpu_before,
            "cpu_end": cpu_after,
            "ram_start_percent": mem_before,
            "ram_end_percent": mem_after,
            "gpu_start_mb": gpu_before,
            "gpu_end_mb": gpu_after,
            "text": text,
        }

        results.append(result)

        print(json.dumps(result, indent=4))
        print("\n----------------------------------------------\n")

    print(" Final Benchmark Results:")
    print(json.dumps(results, indent=4))

    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=4)

    print(" Results saved to benchmark_results.json")


if __name__ == "__main__":
    benchmark()



client.py-
import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json

SERVER_URL = "ws://localhost:8000/ws-asr"
SAMPLE_RATE = 16000
CHUNK = 1024


async def stream_audio():
    async with websockets.connect(SERVER_URL) as ws:
        print("🎤 Speak now... (4 seconds window)")

        loop = asyncio.get_event_loop()

        def callback(indata, frames, time, status):
            asyncio.run_coroutine_threadsafe(
                ws.send(indata.tobytes()), loop
            )

        with sd.InputStream(
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK,
            dtype="int16",
            callback=callback
        ):
            await asyncio.sleep(4)

        await ws.send(b"__END__")

        response = await ws.recv()
        data = json.loads(response)

        print("\n======================")
        print("TRANSCRIPTION:", data["text"])
        print("ASR LATENCY:", data["asr_latency_sec"], "sec")
        print("TOTAL LATENCY:", data["total_end_to_end_sec"], "sec")
        print("FRAMES:", data["frames_received"])
        print("======================")


if __name__ == "__main__":
    asyncio.run(stream_audio())


server.py-
import asyncio
import json
import numpy as np
import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import nemo.collections.asr as nemo_asr
import time
import os

app = FastAPI()

# ---------------------------------------------
# Load NVIDIA Parakeet Real-Time ASR Model
# ---------------------------------------------
print("🔄 Loading ASR model…")
asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name="nvidia/parakeet_realtime_eou_120m-v1"
)
print("Model loaded!")


# ---------------------------------------------
# State Manager (Exact Object)
# ---------------------------------------------
class ASRState:
    def __init__(self, sample_rate=16000):
        self.buffer = []
        self.sample_rate = sample_rate
        self.frames_received = 0
        self.start_time = time.time()

    def add_audio(self, audio_bytes):
        audio = np.frombuffer(audio_bytes, dtype=np.int16)
        self.buffer.append(audio)
        self.frames_received += len(audio)

    def get_audio(self):
        if not self.buffer:
            return None
        data = np.concatenate(self.buffer)
        self.buffer = []
        return data


# ---------------------------------------------
# WebSocket ASR Endpoint
# ---------------------------------------------
@app.websocket("/ws-asr")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state = ASRState()
    print("WebSocket client connected.")

    try:
        while True:
            message = await websocket.receive_bytes()

            if message == b"__END__":
                audio_data = state.get_audio()
                if audio_data is None:
                    await websocket.send_text(json.dumps({"text": ""}))
                    continue

                sf.write("temp.wav", audio_data, state.sample_rate)

                asr_start = time.time()
                output = asr_model.transcribe(["temp.wav"])
                asr_latency = time.time() - asr_start

                text = output[0].text
                total_latency = time.time() - state.start_time

                result = {
                    "text": text,
                    "asr_latency_sec": round(asr_latency, 4),
                    "total_end_to_end_sec": round(total_latency, 4),
                    "frames_received": state.frames_received
                }

                await websocket.send_text(json.dumps(result))
                print("📝 TEXT:", text)
                print("⚡ ASR latency:", result["asr_latency_sec"])
                print("⏱️ Total E2E latency:", result["total_end_to_end_sec"])

                state = ASRState()

            else:
                state.add_audio(message)

    except WebSocketDisconnect:
        print(" Client disconnected.")
    except Exception as e:
        print(" Error:", e)


if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, host="0.0.0.0")


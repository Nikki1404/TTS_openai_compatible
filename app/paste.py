import os
import time
import json
import numpy as np
import soundfile as sf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

# ---------------------------------------------------
# FORCE CPU MODE (NO GPU, NO CUDA)
# ---------------------------------------------------
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import torch
torch.set_default_device("cpu")

import nemo.collections.asr as nemo_asr

app = FastAPI()

# ---------------------------------------------------
# LOAD PARAKEET REALTIME MODEL ON CPU
# ---------------------------------------------------
print("🔄 Loading Parakeet Realtime model on CPU...")
asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name="nvidia/parakeet_realtime_eou_120m-v1",
    map_location="cpu"
)
print("✅ Model loaded on CPU successfully!")


# ---------------------------------------------------
# STATE MANAGER (Exact Object)
# ---------------------------------------------------
class ASRStateCPU:
    def __init__(self, sample_rate=16000):
        self.buffer = []
        self.sample_rate = sample_rate
        self.frames = 0
        self.start_time = time.time()

    def add_audio(self, audio_bytes):
        audio = np.frombuffer(audio_bytes, dtype=np.int16)
        self.buffer.append(audio)
        self.frames += len(audio)

    def get_audio(self):
        if len(self.buffer) == 0:
            return None
        audio = np.concatenate(self.buffer)
        self.buffer = []
        return audio


# ---------------------------------------------------
# WEBSOCKET ENDPOINT
# ---------------------------------------------------
@app.websocket("/ws-asr")
async def ws_asr(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Client connected.")
    state = ASRStateCPU()

    try:
        while True:
            data = await websocket.receive_bytes()

            # END OF UTTERANCE (client triggers)
            if data == b"__END__":
                audio_data = state.get_audio()

                if audio_data is None:
                    await websocket.send_text(json.dumps({"text": ""}))
                    continue

                # Save temp wav file
                sf.write("temp.wav", audio_data, state.sample_rate)

                # CPU ASR inference
                t0 = time.time()
                out = asr_model.transcribe(["temp.wav"])
                asr_latency = time.time() - t0

                text = out[0].text
                total_latency = time.time() - state.start_time

                result = {
                    "text": text,
                    "asr_latency_sec": round(asr_latency, 4),
                    "total_end_to_end_sec": round(total_latency, 4),
                    "frames_received": state.frames
                }

                await websocket.send_text(json.dumps(result))
                print("📝 TEXT:", text)
                print("⚡ ASR Latency:", result["asr_latency_sec"])
                print("⏱️ Total Latency:", result["total_end_to_end_sec"])

                state = ASRStateCPU()  # Reset for next utterance

            else:
                state.add_audio(data)

    except WebSocketDisconnect:
        print("🔴 Client disconnected.")
    except Exception as e:
        print("❌ Error:", str(e))


# ---------------------------------------------------
# RUN SERVER
# ---------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("server_cpu:app", host="0.0.0.0", port=8000)

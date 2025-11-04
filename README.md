# Kokoro OpenAI-Compatible TTS (HTTP-only)

FastAPI server exposing OpenAI-style `/v1/audio/speech` for **Kokoro** (no websockets). Includes an interactive client.

## Run (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export KOKORO_API_KEY=devkey   # optional
uvicorn app.main:app --host 0.0.0.0 --port 8080

## Docker 
docker build -t kokoro-openai-tts:latest .
docker run --rm -p 8080:8080 -e KOKORO_API_KEY=devkey kokoro-openai-tts:latest

How to run in local
uvicorn app.main:app --host 0.0.0.0 --port 8080

Health:

curl http://localhost:8080/healthz

How to test (only curl + OpenAI SDK)
A) Single request, save to file (WAV/MP3/OGG/FLAC)
curl -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Hello from Kokoro","voice":"af_heart","response_format":"mp3"}' \
  --output hello.mp3 && afplay hello.mp3

B) Streaming response (chunked) to file
curl -N -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Streaming hello from Kokoro","voice":"af_heart","response_format":"wav","stream":true}' \
  --output stream.wav && afplay stream.wav

C) Multi-voice blend
curl -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","input":"Blended voices demo","voice":"af_sky+af_bella","response_format":"mp3"}' \
  --output blend.mp3 && afplay blend.mp3

D) Re-use a JSON file (no hardcoding in the command)

Create request.json once:

{
  "model": "tts-1",
  "input": "Read from JSON file.",
  "voice": "af_heart",
  "response_format": "wav",
  "stream": false
}

Send it with curl:

curl -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  --data @request.json \
  --output out.wav && afplay out.wav

E) “Interactive” with curl (type JSON, finish with Ctrl-D)

(No bash scripts; pure curl reading from stdin)
Run:

curl -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  --data-binary @- \
  --output live.wav && afplay live.wav

Then paste one JSON object (you can quickly edit input each time):

{"model":"tts-1","input":"Your free-typed line here","voice":"af_heart","response_format":"mp3","stream":true}

Press Ctrl-D to send. Repeat the same command for the next line.

Test with the OpenAI Python SDK
python3 app/test_openai.py 


## Test
 chmod +x scripts/tts.sh
 ./scripts/tts.sh

## Client (interactive)
python client/client.py --url http://localhost:8080/v1/audio/speech --play --api-key devkey

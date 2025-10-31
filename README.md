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

## Test
curl -sS -X POST http://localhost:8080/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer devkey" \
  -d '{"model":"tts-1","input":"Hello from Kokoro","voice":"af_heart","response_format":"wav","speed":1.0,"lang_code":"a","stream":true}' \
  --output out.wav

## Client (interactive)
python client/client.py --url http://localhost:8080/v1/audio/speech --play --api-key devkey

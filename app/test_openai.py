from openai import OpenAI

client = OpenAI(
    base_url="http://10.90.126.61:8080/v1",
    api_key="not-needed",
)

with client.audio.speech.with_streaming_response.create(
    model="kokoro",                  # or "tts-1" (ignored by server)
    voice="af_sky+af_bella",         # or "af_heart"
    input="Hello world from Kokoro!",
    response_format="mp3",
) as resp:
    resp.stream_to_file("output.mp3")

print("Saved -> output.mp3")

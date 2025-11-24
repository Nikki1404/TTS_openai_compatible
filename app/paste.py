FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

WORKDIR /app

# Step 1: Install system dependencies + Python
RUN apt-get update && apt-get install -y \
    git ffmpeg python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Step 2: Environment variables (AFTER Python exists)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart \
    KOKORO_PRELOAD_VOICES="af_heart af_bella af_sky"


COPY . /app/

RUN --mount=type=cache,target=/root/.cache/pip pip install -r /app/requirements.txt

# Step 4: Install ONNX GPU runtime
RUN pip install onnxruntime-gpu



EXPOSE 8080

# Step 6: Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

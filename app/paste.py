# Use NVIDIA CUDA runtime base image (GPU + CPU fallback)
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python 3.11 + system deps
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip git ffmpeg \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart \
    KOKORO_PRELOAD_VOICES="af_heart af_bella af_sky"

WORKDIR /app

# Copy dependency list and install with caching
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r /app/requirements.txt

# Copy app
COPY app /app/app

EXPOSE 8080

# Launch API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

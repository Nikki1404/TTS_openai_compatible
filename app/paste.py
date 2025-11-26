docker build \
    --build-arg USE_PROXY=true \
    -t kokoro-tts:0.0.1 .

FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------
# Build args (optional proxy)
# -----------------------------
ARG USE_PROXY=false
ARG PROXY_URL="http://163.116.128.80:8080"

# -----------------------------
# Conditional Proxy Setup
# -----------------------------
RUN if [ "$USE_PROXY" = "true" ]; then \
        echo "⚠ Using proxy: $PROXY_URL"; \
        export http_proxy="$PROXY_URL"; \
        export https_proxy="$PROXY_URL"; \
        echo "Acquire::http::Proxy \"$PROXY_URL\";" > /etc/apt/apt.conf.d/99proxy; \
        echo "Acquire::https::Proxy \"$PROXY_URL\";" >> /etc/apt/apt.conf.d/99proxy; \
    else \
        echo "✔ No proxy configured"; \
    fi

# -----------------------------
# Install Python + Dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
        software-properties-common curl \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
        python3.12 python3.12-distutils python3.12-venv \
        ffmpeg build-essential gcc g++ make libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart

WORKDIR /app

# -----------------------------
# Copy only src/ into container
# -----------------------------
COPY src/ /app/

# -----------------------------
# Install Python packages
# -----------------------------
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r /app/requirements.txt

EXPOSE 4000

# Host/port MUST come only from Dockerfile
CMD ["python3", "ws_kokoro_server.py", "--host", "0.0.0.0", "--port", "4000"]


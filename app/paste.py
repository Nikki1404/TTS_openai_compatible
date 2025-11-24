FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev \
    git ffmpeg libsndfile1 espeak-ng \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir onnxruntime-gpu==1.19.0

COPY app /app/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart \
    KOKORO_PRELOAD_VOICES="af_heart af_bella af_sky" \
    DEBIAN_FRONTEND=noninteractive

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]




gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t kokoro-gpu .
us-central1-docker.pkg.dev/emr-dgt-autonomous-uc1r1-snbx/cx-speech/kokoro:latest
docker tag kokoro-gpu \
us-central1-docker.pkg.dev/emr-dgt-autonomous-uc1r1-snbx/cx-speech/kokoro:latest
docker push us-central1-docker.pkg.dev/emr-dgt-autonomous-uc1r1-snbx/cx-speech/kokoro:latest
gcloud run deploy kokoro-gpu \
  --image=us-central1-docker.pkg.dev/emr-dgt-autonomous-uc1r1-snbx/cx-speech/kokoro:latest \
  --platform=managed \
  --region=us-central1 \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --memory=8Gi \
  --timeout=600 \
  --no-cpu-throttling \
  --allow-unauthenticated

gcloud builds submit --tag \
us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro:latest .



https://console.cloud.google.com/artifacts/docker/emr-dgt-autonomous-uctr1-snbx/us-central1/cx-speech?project=emr-dgt-autonomous-uctr1-snbx


gcloud run deploy kokoro-gpu \
  --image=us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro:latest \
  --region=us-central1 \
  --platform=managed \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --memory=8Gi \
  --cpu=2 \
  --timeout=600 \
  --no-cpu-throttling \
  --min-instances=1 \
  --allow-unauthenticated


gcloud config set project emr-dgt-autonomous-uctr1-snbx

gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

gcloud services list --enabled | grep run

gcloud run deploy kokoro-gpu \
  --image=us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro:latest \
  --region=us-central1 \
  --platform=managed \
  --gpu=kind=nvidia-l4,device=0 \
  --cpu=4 \
  --memory=16Gi \
  --timeout=3600 \
  --max-instances=1 \
  --allow-unauthenticated

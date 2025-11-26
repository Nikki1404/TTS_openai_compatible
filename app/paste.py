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

re_nikitav@cloudshell:~/fastapi_impl_gpu (emr-dgt-autonomous-uctr1-snbx)$ gcloud run deploy kokoro-gpu \
  --image=us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro:latest \
  --platform=managed \
  --region=us-central1 \
  --gpu-type=nvidia-l4 \
  --gpu=1 \
  --cpu=4 \
  --memory=16Gi \
  --timeout=3600 \
  --max-instances=1 \
  --allow-unauthenticated
Deploying container to Cloud Run service [kokoro-gpu] in project [emr-dgt-autonomous-uctr1-snbx] region [us-central1]
Deploying new service...failed                                                         --region=us-central1 \
  --gpu-type=nvidia-l4 \
  --gpu=1 \
  --cpu=4 \
  --memory=16Gi \
  --timeout=3600 \
  --max-instances=1 \
  --allow-unauthenticated
Deploying container to Cloud Run service [kokoro-gpu] in project [emr-dgt-autonomous-uctr1-snbx] region [us-central1]
Deploying new service...failed                                                                                                                              
Deployment failed                                                                                                                                           
spec.template.metadata.annotations[autoscaling.knative.dev/maxScale]: You do not have quota for using GPUs with zonal redundancy. Learn more about GPU zonal 
redundancy: g.co/cloudrun/gpu-redundancy-help

To request quota: g.co/cloudrun/gpu-quota

Would you like to deploy with no zonal redundancy instead? (Y/n)?  Y

Deploying new service...                                                                                                                                    
  Setting IAM Policy...done                                                                                                                                 
  Creating Revision...\                                                              redundancy: g.co/cloudrun/gpu-redundancy-help

To request quota: g.co/cloudrun/gpu-quota

Would you like to deploy with no zonal redundancy instead? (Y/n)?  Y

Deploying new service...                                                                                                                                    
  Setting IAM Policy...done                                                                                                                                 
  Creating Revision...\                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  Creating Revision...failed                                                                                                                                
Deployment failed                                                                                                                                           
ERROR: (gcloud.run.deploy) The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout. This can happen when the container port is misconfigured or if the timeout is too short. The health check timeout can be extended. Logs for this revision might contain more information.

Logs URL: https://console.cloud.google.com/logs/viewer?project=emr-dgt-autonomous-uctr1-snbx&resource=cloud_run_revision/service_name/kokoro-gpu/revision_name/kokoro-gpu-00001-lzt&advancedFilter=resource.type%3D%22cloud_run_revision%22%0Aresource.labels.service_name%3D%22kokoro-gpu%22%0Aresource.labels.revision_name%3D%22kokoro-gpu-00001-lzt%22 
For more troubleshooting guidance, see https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start
re_nikitav@cloudshell:~/fastapi_impl_gpu (emr-dgt-autonomous-uctr1-snbx)$ 


gcloud logs read --project=emr-dgt-autonomous-uctr1-snbx --region=us-central1 --service=kokoro-gpu --limit=200
gcloud run deploy kokoro-gpu \
  --image=us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro:latest \
  --platform=managed \
  --region=us-central1 \
  --gpu-type=nvidia-l4 \
  --gpu=1 \
  --cpu=6 \
  --memory=24Gi \
  --timeout=3600 \
  --max-instances=1 \
  --min-instances=1 \
  --no-cpu-throttling \
  --allow-unauthenticated



# app/tts/kokoro_engine.py
import io
import os
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
from pydub import AudioSegment

from app.core.config import settings
from kokoro_tts import KPipeline   s

_PIPELINE: Optional[KPipeline] = None
_LANG_IN_USE: Optional[str] = None


def _get_pipeline(lang_code: str) -> KPipeline:
    global _PIPELINE, _LANG_IN_USE
    if _PIPELINE is None or _LANG_IN_USE != lang_code:
        _PIPELINE = KPipeline(lang_code=lang_code)
        _LANG_IN_USE = lang_code
    return _PIPELINE


def _as_float32_mono(x) -> np.ndarray:
    try:
        import torch
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().numpy()
    except Exception:
        pass

    a = np.asarray(x, dtype=np.float32).reshape(-1)
    return a


def synthesize_np(
    text: str,
    voice: Optional[str] = None,
    speed: float = 1.0,
    lang_code: Optional[str] = None,
    sample_rate: Optional[int] = None,
) -> Tuple[np.ndarray, int]:

    voice = voice or settings.default_voice
    lang_code = lang_code or settings.lang_code
    sr = int(sample_rate or settings.default_sample_rate)

    pipe = _get_pipeline(lang_code=lang_code)

    voices = [v.strip() for v in (voice or "").split("+") if v.strip()] or [
        settings.default_voice
    ]
    rendered = []

    for v in voices:
        chunks = []
        gen = pipe(text, voice=v, speed=float(speed), split_pattern=r"\n+")
        for (_, _, audio) in gen:
            chunks.append(_as_float32_mono(audio))
        if chunks:
            rendered.append(np.concatenate(chunks))

    if not rendered:
        return np.zeros(0, dtype=np.float32), sr

    if len(rendered) == 1:
        return rendered[0], sr

    # Blend multiple voices
    maxlen = max(len(a) for a in rendered)
    out = np.zeros(maxlen, dtype=np.float32)
    for a in rendered:
        if len(a) < maxlen:
            a = np.pad(a, (0, maxlen - len(a)))
        out += a
    out /= float(len(rendered))
    out = np.clip(out, -1.0, 1.0)
    return out, sr


def _encode_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def _encode_flac_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="FLAC")
    return buf.getvalue()


def _encode_ogg_bytes(audio: np.ndarray, sr: int) -> bytes:
    # If soundfile lacks OGG support, fallback to pydub
    try:
        buf = io.BytesIO()
        sf.write(buf, audio, sr, format="OGG", subtype="VORBIS")
        return buf.getvalue()
    except Exception:
        seg = AudioSegment(
            (audio * 32767.0).astype(np.int16).tobytes(),
            frame_rate=sr, sample_width=2, channels=1,
        )
        out = io.BytesIO()
        seg.export(out, format="ogg")
        return out.getvalue()


def _encode_mp3_bytes(audio: np.ndarray, sr: int) -> bytes:
    seg = AudioSegment(
        (audio * 32767.0).astype(np.int16).tobytes(),
        frame_rate=sr, sample_width=2, channels=1,
    )
    out = io.BytesIO()
    seg.export(out, format="mp3")
    return out.getvalue()


def encode_audio(audio: np.ndarray, sr: int, fmt: str):
    fmt = fmt.lower()
    if fmt == "wav":
        return _encode_wav_bytes(audio, sr), "audio/wav"
    if fmt == "flac":
        return _encode_flac_bytes(audio, sr), "audio/flac"
    if fmt == "ogg":
        return _encode_ogg_bytes(audio, sr), "audio/ogg"
    if fmt == "mp3":
        return _encode_mp3_bytes(audio, sr), "audio/mpeg"
    if fmt == "pcm":
        pcm16 = (audio * 32767.0).astype(np.int16).tobytes()
        return pcm16, "audio/pcm"

    return _encode_wav_bytes(audio, sr), "audio/wav"


def maybe_save(audio: np.ndarray, sr: int, basename: str, enable: bool):
    if not enable:
        return None

    os.makedirs(settings.save_dir, exist_ok=True)
    out = os.path.join(settings.save_dir, f"{basename}.wav")
    sf.write(out, audio, sr, "PCM_16")
    return out

#9 143.3   Using cached language_tags-1.2.0-py3-none-any.whl (213 kB)
#9 143.4 Collecting rfc3986<2
#9 143.4   Using cached rfc3986-1.5.0-py2.py3-none-any.whl (31 kB)
#9 143.5 Collecting python-dateutil
#9 143.5   Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
#9 143.6 Collecting jsonschema
#9 143.6   Using cached jsonschema-4.25.1-py3-none-any.whl (90 kB)
#9 143.7 Collecting termcolor
#9 143.7   Using cached termcolor-3.2.0-py3-none-any.whl (7.7 kB)
#9 143.7 Collecting isodate
#9 143.8   Using cached isodate-0.7.2-py3-none-any.whl (22 kB)
#9 144.4 Collecting wrapt
#9 144.4   Using cached wrapt-2.0.1-cp310-cp310-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (113 kB)
#9 144.6 Collecting jsonschema-specifications>=2023.03.6
#9 144.6   Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
#9 144.7 Collecting referencing>=0.28.4
#9 144.8   Using cached referencing-0.37.0-py3-none-any.whl (26 kB)
#9 145.9 Collecting rpds-py>=0.7.1
#9 146.0   Using cached rpds_py-0.29.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (392 kB)
#9 146.1 Collecting six>=1.5
#9 146.1   Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
#9 146.3 Collecting pyparsing<4,>=2.1.0
#9 146.3   Using cached pyparsing-3.2.5-py3-none-any.whl (113 kB)
#9 146.5 ERROR: Exception:
#9 146.5 Traceback (most recent call last):
#9 146.5   File "/usr/lib/python3/dist-packages/pip/_internal/cli/base_command.py", line 165, in exc_logging_wrapper
#9 146.5     status = run_func(*args)
#9 146.5   File "/usr/lib/python3/dist-packages/pip/_internal/cli/req_command.py", line 205, in wrapper
#9 146.5     return func(self, options, args)
#9 146.5   File "/usr/lib/python3/dist-packages/pip/_internal/commands/install.py", line 389, in run
#9 146.5     to_install = resolver.get_installation_order(requirement_set)
#9 146.5   File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 188, in get_installation_order
#9 146.5     weights = get_topological_weights(
#9 146.5   File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 276, in get_topological_weights
#9 146.5     assert len(weights) == expected_node_count
#9 146.5 AssertionError
#9 ERROR: process "/bin/sh -c pip install -r /app/requirements.txt" did not complete successfully: exit code: 2
------
 > [stage-0 5/6] RUN --mount=type=cache,target=/root/.cache/pip pip install -r /app/requirements.txt:
146.5     status = run_func(*args)
146.5   File "/usr/lib/python3/dist-packages/pip/_internal/cli/req_command.py", line 205, in wrapper
146.5     return func(self, options, args)
146.5   File "/usr/lib/python3/dist-packages/pip/_internal/commands/install.py", line 389, in run
146.5     to_install = resolver.get_installation_order(requirement_set)
146.5   File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 188, in get_installation_order
146.5     weights = get_topological_weights(
146.5   File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 276, in get_topological_weights
146.5     assert len(weights) == expected_node_count
146.5 AssertionError
------
Dockerfile:19
--------------------
  17 |     COPY . /app/
  18 |     
  19 | >>> RUN --mount=type=cache,target=/root/.cache/pip pip install -r /app/requirements.txt


FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev \
    git ffmpeg libsndfile1 espeak-ng \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

COPY app /app/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart \
    KOKORO_PRELOAD_VOICES="af_heart af_bella af_sky" \
    CUDA_MODULE_LOADING=LAZY \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

EXPOSE 8081

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]

us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-speech/kokoro 


curl --location --request POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
  --header "Content-Type: application/json" \
  --data '{
    "message": {
        "conversationId": "200412",
        "speaker": "user",
        "agentType": "dfcx",
        "transcript": "Hey",
        "hm-conversation-metadata": {
            "agentData": {
                "qualityScore": "1",
                "experienceYears": "1",
                "agentName": "max weber"
            },
            "ccaasData": {
                "check1": true,
                "check2": "verified"
            },
            "intervention": "No escalation needed"
        }
    }
  }'

curl -X POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "conversationId": "CID-TEST-001",
      "speaker": "agent",
      "transcript": "This is a test entry for hm-conversation-metadata.",
      "agentType": "BOT",
      "hm-conversation-metadata": {
        "agentData": {
          "agentName": "Nikita",
          "qualityScore": 98
        },
        "ccaasData": {
          "ck1": true,
          "category": "verification"
        },
        "intervention": "No escalation needed"
      }
    }
  }'


gcloud container clusters get-credentials kokoro-cluster \
    --zone us-central1-a \
    --project emr-dgt-autonomous-uctr1-snbx


kubectl apply -f k8s/

kubectl get pods -o wide

kubectl get svc kokoro-service

FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ENV https_proxy="http://163.116.128.80:8080"
ENV http_proxy="http://163.116.128.80:8080"

RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update && apt-get install -y \
        python3.12 \
        python3.12-distutils \
        python3.12-venv \
        ffmpeg \
        build-essential gcc g++ make \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KOKORO_LANG=a \
    KOKORO_DEFAULT_VOICE=af_heart \
    KOKORO_PRELOAD_VOICES="af_heart af_bella af_sky"

WORKDIR /app

COPY . /app/

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install -r /app/requirements.txt

EXPOSE 4000

CMD ["python3", "ws_kokoro_server:app", "--host", "0.0.0.0", "--port", "4000"]
    

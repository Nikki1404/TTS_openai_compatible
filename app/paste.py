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

Traceback (most recent call last):
  File "/usr/local/bin/uvicorn", line 8, in <module>
    sys.exit(main())
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1485, in __call__
    return self.main(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1406, in main
    rv = self.invoke(ctx)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 1269, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/usr/local/lib/python3.10/dist-packages/click/core.py", line 824, in invoke
    return callback(*args, **kwargs)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/main.py", line 423, in main
    run(
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/main.py", line 593, in run
    server.run()
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 67, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/_compat.py", line 60, in asyncio_run
    return loop.run_until_complete(main)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 71, in serve
    await self._serve(sockets)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/server.py", line 78, in _serve
    config.load()
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/config.py", line 439, in load
    self.loaded_app = import_from_string(self.app)
  File "/usr/local/lib/python3.10/dist-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 883, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/app/main.py", line 4, in <module>
    from app.routers.openai_compatible import router as openai_router
  File "/app/app/routers/openai_compatible.py", line 8, in <module>
    from app.tts.kokoro_engine import synthesize_np, encode_audio, maybe_save
  File "/app/app/tts/kokoro_engine.py", line 12, in <module>
    from kokoro_tts import KPipeline
  File "/usr/local/lib/python3.10/dist-packages/kokoro_tts/__init__.py", line 20, in <module>
    import sounddevice as sd
  File "/usr/local/lib/python3.10/dist-packages/sounddevice.py", line 71, in <module>
    raise OSError('PortAudio library not found')
OSError: PortAudio library not found"

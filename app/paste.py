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
Step 5/10 : RUN pip install --no-cache-dir -r /app/requirements.txt
 Running in 77bbb4496fa4
Collecting fastapi
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 561
DEBUG: Reading GCS logfile: 206 (read 561 bytes)
  Downloading fastapi-0.121.3-py3-none-any.whl (109 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 109.8/109.8 KB 4.2 MB/s eta 0:00:00
Collecting uvicorn
  Downloading uvicorn-0.38.0-py3-none-any.whl (68 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68.1/68.1 KB 51.2 MB/s eta 0:00:00
Collecting numpy
  Downloading numpy-2.2.6-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (16.8 MB)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1532
DEBUG: Reading GCS logfile: 206 (read 1532 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 16.8/16.8 MB 55.2 MB/s eta 0:00:00
Collecting openai
  Downloading openai-2.8.1-py3-none-any.whl (1.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.0/1.0 MB 119.6 MB/s eta 0:00:00
Collecting pydub
  Downloading pydub-0.25.1-py2.py3-none-any.whl (32 kB)
Collecting requests
  Downloading requests-2.32.5-py3-none-any.whl (64 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 64.7/64.7 KB 183.4 MB/s eta 0:00:00
Collecting pydantic-settings
  Downloading pydantic_settings-2.12.0-py3-none-any.whl (51 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 51.9/51.9 KB 162.0 MB/s eta 0:00:00
Collecting kokoro
  Downloading kokoro-0.9.4-py3-none-any.whl (32 kB)
Collecting typing-extensions>=4.8.0
  Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 44.6/44.6 KB 128.7 MB/s eta 0:00:00
Collecting starlette<0.51.0,>=0.40.0
  Downloading starlette-0.50.0-py3-none-any.whl (74 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 74.0/74.0 KB 131.6 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1806
DEBUG: Reading GCS logfile: 206 (read 1806 bytes)
Collecting pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4
  Downloading pydantic-2.12.4-py3-none-any.whl (463 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 463.4/463.4 KB 247.1 MB/s eta 0:00:00
Collecting annotated-doc>=0.0.2
  Downloading annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
Collecting click>=7.0
  Downloading click-8.3.1-py3-none-any.whl (108 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 108.3/108.3 KB 217.6 MB/s eta 0:00:00
Collecting h11>=0.8
  Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Collecting distro<2,>=1.7.0
  Downloading distro-1.9.0-py3-none-any.whl (20 kB)
Collecting sniffio
  Downloading sniffio-1.3.1-py3-none-any.whl (10 kB)
Collecting jiter<1,>=0.10.0
  Downloading jiter-0.12.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (364 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 364.4/364.4 KB 269.6 MB/s eta 0:00:00
Collecting anyio<5,>=3.5.0
  Downloading anyio-4.11.0-py3-none-any.whl (109 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 109.1/109.1 KB 225.8 MB/s eta 0:00:00
Collecting httpx<1,>=0.23.0
  Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 73.5/73.5 KB 178.7 MB/s eta 0:00:00
Collecting tqdm>4
  Downloading tqdm-4.67.1-py3-none-any.whl (78 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.5/78.5 KB 203.2 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1806
DEBUG: Reading GCS logfile: 206 (read 1806 bytes)
Collecting certifi>=2017.4.17
  Downloading certifi-2025.11.12-py3-none-any.whl (159 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 159.4/159.4 KB 238.9 MB/s eta 0:00:00
Collecting idna<4,>=2.5
  Downloading idna-3.11-py3-none-any.whl (71 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 71.0/71.0 KB 203.7 MB/s eta 0:00:00
Collecting urllib3<3,>=1.21.1
  Downloading urllib3-2.5.0-py3-none-any.whl (129 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 129.8/129.8 KB 240.9 MB/s eta 0:00:00
Collecting charset_normalizer<4,>=2
  Downloading charset_normalizer-3.4.4-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (153 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 153.6/153.6 KB 261.9 MB/s eta 0:00:00
Collecting typing-inspection>=0.4.0
  Downloading typing_inspection-0.4.2-py3-none-any.whl (14 kB)
Collecting python-dotenv>=0.21.0
  Downloading python_dotenv-1.2.1-py3-none-any.whl (21 kB)
Collecting transformers
  Downloading transformers-4.57.1-py3-none-any.whl (12.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.0/12.0 MB 116.5 MB/s eta 0:00:00
Collecting huggingface-hub
  Downloading huggingface_hub-1.1.5-py3-none-any.whl (516 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 516.0/516.0 KB 268.6 MB/s eta 0:00:00
Collecting torch
  Downloading torch-2.9.1-cp310-cp310-manylinux_2_28_x86_64.whl (899.8 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 957
DEBUG: Reading GCS logfile: 206 (read 957 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 899.8/899.8 MB 158.0 MB/s eta 0:00:00
Collecting loguru
  Downloading loguru-0.7.3-py3-none-any.whl (61 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 61.6/61.6 KB 202.1 MB/s eta 0:00:00
Collecting misaki[en]>=0.9.4
  Downloading misaki-0.9.4-py3-none-any.whl (3.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.6/3.6 MB 187.5 MB/s eta 0:00:00
Collecting exceptiongroup>=1.0.2
  Downloading exceptiongroup-1.3.1-py3-none-any.whl (16 kB)
Collecting httpcore==1.*
  Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.8/78.8 KB 189.7 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1673
DEBUG: Reading GCS logfile: 206 (read 1673 bytes)
Collecting addict
  Downloading addict-2.4.0-py3-none-any.whl (3.8 kB)
Collecting regex
  Downloading regex-2025.11.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (791 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 791.7/791.7 KB 262.6 MB/s eta 0:00:00
Collecting phonemizer-fork
  Downloading phonemizer_fork-3.3.2-py3-none-any.whl (82 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 82.7/82.7 KB 198.2 MB/s eta 0:00:00
Collecting num2words
  Downloading num2words-0.5.14-py3-none-any.whl (163 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 163.5/163.5 KB 247.2 MB/s eta 0:00:00
Collecting spacy-curated-transformers
  Downloading spacy_curated_transformers-2.1.2-py2.py3-none-any.whl (240 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 240.3/240.3 KB 258.3 MB/s eta 0:00:00
Collecting espeakng-loader
  Downloading espeakng_loader-0.2.4-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (10.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.1/10.1 MB 161.5 MB/s eta 0:00:00
Collecting spacy
  Downloading spacy-3.8.11-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (31.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 31.0/31.0 MB 153.7 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 716
DEBUG: Reading GCS logfile: 206 (read 716 bytes)
Collecting pydantic-core==2.41.5
  Downloading pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 166.8 MB/s eta 0:00:00
Collecting annotated-types>=0.6.0
  Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Collecting fsspec>=2023.5.0
  Downloading fsspec-2025.10.0-py3-none-any.whl (200 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 201.0/201.0 KB 239.2 MB/s eta 0:00:00
Collecting shellingham
  Downloading shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1504
DEBUG: Reading GCS logfile: 206 (read 1504 bytes)
Collecting typer-slim
  Downloading typer_slim-0.20.0-py3-none-any.whl (47 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 47.1/47.1 KB 173.5 MB/s eta 0:00:00
Collecting filelock
  Downloading filelock-3.20.0-py3-none-any.whl (16 kB)
Collecting hf-xet<2.0.0,>=1.2.0
  Downloading hf_xet-1.2.0-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.3/3.3 MB 175.4 MB/s eta 0:00:00
Collecting pyyaml>=5.1
  Downloading pyyaml-6.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (770 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 770.3/770.3 KB 287.5 MB/s eta 0:00:00
Collecting packaging>=20.9
  Downloading packaging-25.0-py3-none-any.whl (66 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 66.5/66.5 KB 186.3 MB/s eta 0:00:00
Collecting networkx>=2.5.1
  Downloading networkx-3.4.2-py3-none-any.whl (1.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.7/1.7 MB 233.1 MB/s eta 0:00:00
Collecting nvidia-curand-cu12==10.3.9.90
  Downloading nvidia_curand_cu12-10.3.9.90-py3-none-manylinux_2_27_x86_64.whl (63.6 MB)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 816
DEBUG: Reading GCS logfile: 206 (read 816 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 63.6/63.6 MB 161.4 MB/s eta 0:00:00
Collecting nvidia-nvshmem-cu12==3.3.20
  Downloading nvidia_nvshmem_cu12-3.3.20-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (124.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 124.7/124.7 MB 162.6 MB/s eta 0:00:00
Collecting jinja2
  Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.9/134.9 KB 235.2 MB/s eta 0:00:00
Collecting nvidia-cusparselt-cu12==0.7.1
  Downloading nvidia_cusparselt_cu12-0.7.1-py3-none-manylinux2014_x86_64.whl (287.2 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 155
DEBUG: Reading GCS logfile: 206 (read 155 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 287.2/287.2 MB 170.3 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 134
DEBUG: Reading GCS logfile: 206 (read 134 bytes)
Collecting nvidia-cusolver-cu12==11.7.3.90
  Downloading nvidia_cusolver_cu12-11.7.3.90-py3-none-manylinux_2_27_x86_64.whl (267.5 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 155
DEBUG: Reading GCS logfile: 206 (read 155 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 267.5/267.5 MB 176.3 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 128
DEBUG: Reading GCS logfile: 206 (read 128 bytes)
Collecting nvidia-cublas-cu12==12.8.4.1
  Downloading nvidia_cublas_cu12-12.8.4.1-py3-none-manylinux_2_27_x86_64.whl (594.3 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 283
DEBUG: Reading GCS logfile: 206 (read 283 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 594.3/594.3 MB 203.4 MB/s eta 0:00:00
Collecting nvidia-cudnn-cu12==9.10.2.21
  Downloading nvidia_cudnn_cu12-9.10.2.21-py3-none-manylinux_2_27_x86_64.whl (706.8 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 155
DEBUG: Reading GCS logfile: 206 (read 155 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 706.8/706.8 MB 202.1 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 743
DEBUG: Reading GCS logfile: 206 (read 743 bytes)
Collecting nvidia-cuda-nvrtc-cu12==12.8.93
  Downloading nvidia_cuda_nvrtc_cu12-12.8.93-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl (88.0 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 88.0/88.0 MB 201.3 MB/s eta 0:00:00
Collecting nvidia-cufile-cu12==1.13.1.3
  Downloading nvidia_cufile_cu12-1.13.1.3-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 271.5 MB/s eta 0:00:00
Collecting triton==3.5.1
  Downloading triton-3.5.1-cp310-cp310-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl (170.3 MB)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 296
DEBUG: Reading GCS logfile: 206 (read 296 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 170.3/170.3 MB 194.5 MB/s eta 0:00:00
Collecting nvidia-nccl-cu12==2.27.5
  Downloading nvidia_nccl_cu12-2.27.5-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (322.3 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 542
DEBUG: Reading GCS logfile: 206 (read 542 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 322.3/322.3 MB 220.3 MB/s eta 0:00:00
Collecting sympy>=1.13.3
  Downloading sympy-1.14.0-py3-none-any.whl (6.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.3/6.3 MB 217.1 MB/s eta 0:00:00
Collecting nvidia-cufft-cu12==11.3.3.83
  Downloading nvidia_cufft_cu12-11.3.3.83-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (193.1 MB)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 933
DEBUG: Reading GCS logfile: 206 (read 933 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 193.1/193.1 MB 210.8 MB/s eta 0:00:00
Collecting nvidia-cuda-runtime-cu12==12.8.90
  Downloading nvidia_cuda_runtime_cu12-12.8.90-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (954 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 954.8/954.8 KB 293.5 MB/s eta 0:00:00
Collecting nvidia-nvjitlink-cu12==12.8.93
  Downloading nvidia_nvjitlink_cu12-12.8.93-py3-none-manylinux2010_x86_64.manylinux_2_12_x86_64.whl (39.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 39.3/39.3 MB 222.5 MB/s eta 0:00:00
Collecting nvidia-cusparse-cu12==12.5.8.93
  Downloading nvidia_cusparse_cu12-12.5.8.93-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (288.2 MB)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 155
DEBUG: Reading GCS logfile: 206 (read 155 bytes)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 288.2/288.2 MB 190.7 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 857
DEBUG: Reading GCS logfile: 206 (read 857 bytes)
Collecting nvidia-nvtx-cu12==12.8.90
  Downloading nvidia_nvtx_cu12-12.8.90-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (89 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.0/90.0 KB 218.2 MB/s eta 0:00:00
Collecting nvidia-cuda-cupti-cu12==12.8.90
  Downloading nvidia_cuda_cupti_cu12-12.8.90-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (10.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.2/10.2 MB 220.0 MB/s eta 0:00:00
Collecting huggingface-hub
  Downloading huggingface_hub-0.36.0-py3-none-any.whl (566 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 566.1/566.1 KB 286.9 MB/s eta 0:00:00
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 818
DEBUG: Reading GCS logfile: 206 (read 818 bytes)
Collecting safetensors>=0.4.3
  Downloading safetensors-0.7.0-cp38-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (507 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 507.2/507.2 KB 287.8 MB/s eta 0:00:00
Collecting tokenizers<=0.23.0,>=0.22.0
  Downloading tokenizers-0.22.1-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.3/3.3 MB 232.5 MB/s eta 0:00:00
Collecting mpmath<1.4,>=1.1.0
  Downloading mpmath-1.3.0-py3-none-any.whl (536 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 536.2/536.2 KB 286.4 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1291
DEBUG: Reading GCS logfile: 206 (read 1291 bytes)
Collecting MarkupSafe>=2.0
  Downloading markupsafe-3.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (20 kB)
Collecting docopt>=0.6.2
  Downloading docopt-0.6.2.tar.gz (25 kB)
  Preparing metadata (setup.py): started
  Preparing metadata (setup.py): finished with status 'done'
Collecting attrs>=18.1
  Downloading attrs-25.4.0-py3-none-any.whl (67 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 67.6/67.6 KB 182.5 MB/s eta 0:00:00
Collecting dlinfo
  Downloading dlinfo-2.0.0-py3-none-any.whl (3.7 kB)
Collecting joblib
  Downloading joblib-1.5.2-py3-none-any.whl (308 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 308.4/308.4 KB 271.2 MB/s eta 0:00:00
Collecting segments
  Downloading segments-2.3.0-py2.py3-none-any.whl (15 kB)
Collecting murmurhash<1.1.0,>=0.28.0
  Downloading murmurhash-1.0.15-cp310-cp310-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl (122 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 122.6/122.6 KB 223.0 MB/s eta 0:00:00
Collecting catalogue<2.1.0,>=2.0.6
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 7149
DEBUG: Reading GCS logfile: 206 (read 7149 bytes)
  Downloading catalogue-2.0.10-py3-none-any.whl (17 kB)
Collecting cymem<2.1.0,>=2.0.2
  Downloading cymem-2.0.13-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (229 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.7/229.7 KB 245.7 MB/s eta 0:00:00
Collecting spacy-loggers<2.0.0,>=1.0.0
  Downloading spacy_loggers-1.0.5-py3-none-any.whl (22 kB)
Collecting weasel<0.5.0,>=0.4.2
  Downloading weasel-0.4.3-py3-none-any.whl (50 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.8/50.8 KB 162.7 MB/s eta 0:00:00
Collecting srsly<3.0.0,>=2.4.3
  Downloading srsly-2.5.2-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 296.0 MB/s eta 0:00:00
Collecting wasabi<1.2.0,>=0.9.1
  Downloading wasabi-1.1.3-py3-none-any.whl (27 kB)
Collecting preshed<3.1.0,>=3.0.2
  Downloading preshed-3.0.12-cp310-cp310-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl (780 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 780.3/780.3 KB 231.4 MB/s eta 0:00:00
Collecting spacy-legacy<3.1.0,>=3.0.11
  Downloading spacy_legacy-3.0.12-py2.py3-none-any.whl (29 kB)
Collecting thinc<8.4.0,>=8.3.4
  Downloading thinc-8.3.10-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (3.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.9/3.9 MB 233.7 MB/s eta 0:00:00
Requirement already satisfied: setuptools in /usr/lib/python3/dist-packages (from spacy->misaki[en]>=0.9.4->kokoro->-r /app/requirements.txt (line 8)) (59.6.0)
Collecting curated-tokenizers<3.0.0,>=2.0.0
  Downloading curated_tokenizers-2.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (772 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 772.8/772.8 KB 291.5 MB/s eta 0:00:00
Collecting curated-transformers<3.0.0,>=2.0.0
  Downloading curated_transformers-2.0.1-py2.py3-none-any.whl (363 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 363.5/363.5 KB 283.8 MB/s eta 0:00:00
Collecting spacy-curated-transformers
  Downloading spacy_curated_transformers-2.1.1-py2.py3-none-any.whl (240 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 240.3/240.3 KB 223.8 MB/s eta 0:00:00
Collecting spacy
  Downloading spacy-4.0.0.dev3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (6.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.7/6.7 MB 175.6 MB/s eta 0:00:00
Collecting spacy-curated-transformers
  Downloading spacy_curated_transformers-2.0.0-py2.py3-none-any.whl (240 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 240.3/240.3 KB 272.2 MB/s eta 0:00:00
  Downloading spacy_curated_transformers-0.3.1-py2.py3-none-any.whl (237 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 237.9/237.9 KB 277.3 MB/s eta 0:00:00
Collecting curated-tokenizers<0.1.0,>=0.0.9
  Downloading curated_tokenizers-0.0.9-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (731 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 731.6/731.6 KB 306.2 MB/s eta 0:00:00
Collecting curated-transformers<0.2.0,>=0.1.0
  Downloading curated_transformers-0.1.1-py2.py3-none-any.whl (25 kB)
Collecting blis<1.4.0,>=1.3.0
  Downloading blis-1.3.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (11.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.3/11.3 MB 208.0 MB/s eta 0:00:00
Collecting confection<1.0.0,>=0.0.1
  Downloading confection-0.1.5-py3-none-any.whl (35 kB)
Collecting cloudpathlib<1.0.0,>=0.7.0
  Downloading cloudpathlib-0.23.0-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.8/62.8 KB 193.2 MB/s eta 0:00:00
Collecting smart-open<8.0.0,>=5.2.1
  Downloading smart_open-7.5.0-py3-none-any.whl (63 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 63.9/63.9 KB 173.4 MB/s eta 0:00:00
Collecting csvw>=1.5.6
  Downloading csvw-3.7.0-py2.py3-none-any.whl (60 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.7/60.7 KB 183.5 MB/s eta 0:00:00
Collecting language-tags
  Downloading language_tags-1.2.0-py3-none-any.whl (213 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 213.4/213.4 KB 248.7 MB/s eta 0:00:00
Collecting rdflib
  Downloading rdflib-7.4.0-py3-none-any.whl (569 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 569.0/569.0 KB 305.8 MB/s eta 0:00:00
Collecting rfc3986<2
  Downloading rfc3986-1.5.0-py2.py3-none-any.whl (31 kB)
Collecting babel
  Downloading babel-2.17.0-py3-none-any.whl (10.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.2/10.2 MB 205.0 MB/s eta 0:00:00
Collecting uritemplate>=3.0.0
  Downloading uritemplate-4.2.0-py3-none-any.whl (11 kB)
Collecting isodate
  Downloading isodate-0.7.2-py3-none-any.whl (22 kB)
Collecting jsonschema
  Downloading jsonschema-4.25.1-py3-none-any.whl (90 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.0/90.0 KB 216.4 MB/s eta 0:00:00
Collecting python-dateutil
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.9/229.9 KB 274.4 MB/s eta 0:00:00
Collecting termcolor
  Downloading termcolor-3.2.0-py3-none-any.whl (7.7 kB)
Collecting wrapt
  Downloading wrapt-2.0.1-cp310-cp310-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (113 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 113.7/113.7 KB 195.7 MB/s eta 0:00:00
Collecting rpds-py>=0.7.1
  Downloading rpds_py-0.29.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (392 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 392.7/392.7 KB 260.6 MB/s eta 0:00:00
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 1833
DEBUG: Reading GCS logfile: 206 (read 1833 bytes)
Collecting jsonschema-specifications>=2023.03.6
  Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Collecting referencing>=0.28.4
  Downloading referencing-0.37.0-py3-none-any.whl (26 kB)
Collecting six>=1.5
  Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Collecting pyparsing<4,>=2.1.0
  Downloading pyparsing-3.2.5-py3-none-any.whl (113 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 113.9/113.9 KB 214.7 MB/s eta 0:00:00
Building wheels for collected packages: docopt
  Building wheel for docopt (setup.py): started
  Building wheel for docopt (setup.py): finished with status 'done'
  Created wheel for docopt: filename=docopt-0.6.2-py2.py3-none-any.whl size=13723 sha256=67ecc2041fbc1255f6e9beb32ad23f41482d30b4baba298c025893faceb92728
  Stored in directory: /tmp/pip-ephem-wheel-cache-cac7uutr/wheels/fc/ab/d4/5da2067ac95b36618c629a5f93f809425700506f72c9732fac
Successfully built docopt
ERROR: Exception:
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/pip/_internal/cli/base_command.py", line 165, in exc_logging_wrapper
    status = run_func(*args)
  File "/usr/lib/python3/dist-packages/pip/_internal/cli/req_command.py", line 205, in wrapper
    return func(self, options, args)
  File "/usr/lib/python3/dist-packages/pip/_internal/commands/install.py", line 389, in run
    to_install = resolver.get_installation_order(requirement_set)
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 188, in get_installation_order
    weights = get_topological_weights(
  File "/usr/lib/python3/dist-packages/pip/_internal/resolution/resolvelib/resolver.py", line 276, in get_topological_weights
    assert len(weights) == expected_node_count
AssertionError
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 206 217
DEBUG: Reading GCS logfile: 206 (read 217 bytes)
The command '/bin/sh -c pip install --no-cache-dir -r /app/requirements.txt' returned a non-zero code: 2
ERROR
ERROR: build step 0 "gcr.io/cloud-builders/gcb-internal" failed: step exited with non-zero status: 2

DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://cloudbuild.googleapis.com:443 "GET /v1/projects/emr-dgt-autonomous-uctr1-snbx/locations/global/builds/fcc9825e-92c0-43c6-b520-688ed6d606eb?alt=json HTTP/1.1" 200 None
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
DEBUG: https://storage.googleapis.com:443 "GET /150916788856.cloudbuild-logs.googleusercontent.com/log-fcc9825e-92c0-43c6-b520-688ed6d606eb.txt HTTP/1.1" 416 169
DEBUG: Reading GCS logfile: 416 (no new content; keep polling)
-------------------------------------------------------------------------------------------------------------------------------------------------------------

BUILD FAILURE: Build step failure: build step 0 "gcr.io/cloud-builders/gcb-internal" failed: step exited with non-zero status: 2
DEBUG: (gcloud.builds.submit) build fcc9825e-92c0-43c6-b520-688ed6d606eb completed with status "FAILURE"
Traceback (most recent call last):
  File "/usr/bin/../lib/google-cloud-sdk/lib/googlecloudsdk/calliope/cli.py", line 944, in Execute
    resources = calliope_command.Run(cli=self, args=args)
  File "/usr/bin/../lib/google-cloud-sdk/lib/googlecloudsdk/calliope/backend.py", line 955, in Run
    resources = command_instance.Run(args)
  File "/usr/bin/../lib/google-cloud-sdk/lib/surface/builds/submit.py", line 272, in Run
    build, _ = submit_util.Build(
               ~~~~~~~~~~~~~~~~~^
        messages,
        ^^^^^^^^^
    ...<4 lines>...
        suppress_logs=args.suppress_logs,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        polling_interval=args.polling_interval)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/bin/../lib/google-cloud-sdk/lib/googlecloudsdk/command_lib/builds/submit_util.py", line 940, in Build
    raise FailedBuildException(build)
googlecloudsdk.command_lib.builds.submit_util.FailedBuildException: build fcc9825e-92c0-43c6-b520-688ed6d606eb completed with status "FAILURE"
ERROR: (gcloud.builds.submit) build fcc9825e-92c0-43c6-b520-688ed6d606eb completed with status "FAILURE"
re_nikitav@cloudshell:~/fastapi_impl_gpu (emr-dgt-autonomous-uctr1-snbx)$ 

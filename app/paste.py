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
Collecting weasel<0.5.0,>=0.4.2
  Downloading weasel-0.4.3-py3-none-any.whl (50 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.8/50.8 KB 186.8 MB/s eta 0:00:00
Collecting spacy-loggers<2.0.0,>=1.0.0
  Downloading spacy_loggers-1.0.5-py3-none-any.whl (22 kB)
Requirement already satisfied: setuptools in /usr/lib/python3/dist-packages (from spacy->misaki[en]>=0.9.4->kokoro->-r /app/requirements.txt (line 8)) (59.6.0)
Collecting cymem<2.1.0,>=2.0.2
  Downloading cymem-2.0.13-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (229 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.7/229.7 KB 295.9 MB/s eta 0:00:00
Collecting thinc<8.4.0,>=8.3.4
  Downloading thinc-8.3.10-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (3.9 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.9/3.9 MB 288.9 MB/s eta 0:00:00
Collecting wasabi<1.2.0,>=0.9.1
  Downloading wasabi-1.1.3-py3-none-any.whl (27 kB)
Collecting catalogue<2.1.0,>=2.0.6
  Downloading catalogue-2.0.10-py3-none-any.whl (17 kB)
Collecting preshed<3.1.0,>=3.0.2
  Downloading preshed-3.0.12-cp310-cp310-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl (780 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 780.3/780.3 KB 321.4 MB/s eta 0:00:00
Collecting srsly<3.0.0,>=2.4.3
  Downloading srsly-2.5.2-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (1.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 326.6 MB/s eta 0:00:00
Collecting murmurhash<1.1.0,>=0.28.0
  Downloading murmurhash-1.0.15-cp310-cp310-manylinux1_x86_64.manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_5_x86_64.whl (122 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 122.6/122.6 KB 280.8 MB/s eta 0:00:00
Collecting curated-transformers<3.0.0,>=2.0.0
  Downloading curated_transformers-2.0.1-py2.py3-none-any.whl (363 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 363.5/363.5 KB 73.7 MB/s eta 0:00:00
Collecting curated-tokenizers<3.0.0,>=2.0.0
  Downloading curated_tokenizers-2.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (772 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 772.8/772.8 KB 277.4 MB/s eta 0:00:00
Collecting spacy-curated-transformers
  Downloading spacy_curated_transformers-2.1.1-py2.py3-none-any.whl (240 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 240.3/240.3 KB 290.0 MB/s eta 0:00:00
Collecting spacy
  Downloading spacy-4.0.0.dev3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (6.7 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.7/6.7 MB 211.2 MB/s eta 0:00:00
Collecting spacy-curated-transformers
  Downloading spacy_curated_transformers-2.0.0-py2.py3-none-any.whl (240 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 240.3/240.3 KB 299.8 MB/s eta 0:00:00
  Downloading spacy_curated_transformers-0.3.1-py2.py3-none-any.whl (237 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 237.9/237.9 KB 298.0 MB/s eta 0:00:00
Collecting curated-tokenizers<0.1.0,>=0.0.9
  Downloading curated_tokenizers-0.0.9-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (731 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 731.6/731.6 KB 316.9 MB/s eta 0:00:00
Collecting curated-transformers<0.2.0,>=0.1.0
  Downloading curated_transformers-0.1.1-py2.py3-none-any.whl (25 kB)
Collecting confection<1.0.0,>=0.0.1
  Downloading confection-0.1.5-py3-none-any.whl (35 kB)
Collecting blis<1.4.0,>=1.3.0
  Downloading blis-1.3.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (11.3 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.3/11.3 MB 275.6 MB/s eta 0:00:00
Collecting cloudpathlib<1.0.0,>=0.7.0
  Downloading cloudpathlib-0.23.0-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.8/62.8 KB 223.7 MB/s eta 0:00:00
Collecting smart-open<8.0.0,>=5.2.1
  Downloading smart_open-7.5.0-py3-none-any.whl (63 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 63.9/63.9 KB 232.3 MB/s eta 0:00:00
Collecting csvw>=1.5.6
  Downloading csvw-3.7.0-py2.py3-none-any.whl (60 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.7/60.7 KB 234.4 MB/s eta 0:00:00
Collecting babel
  Downloading babel-2.17.0-py3-none-any.whl (10.2 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.2/10.2 MB 255.2 MB/s eta 0:00:00
Collecting language-tags
  Downloading language_tags-1.2.0-py3-none-any.whl (213 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 213.4/213.4 KB 303.6 MB/s eta 0:00:00
Collecting rdflib
  Downloading rdflib-7.4.0-py3-none-any.whl (569 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 569.0/569.0 KB 301.4 MB/s eta 0:00:00
Collecting python-dateutil
  Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 229.9/229.9 KB 214.3 MB/s eta 0:00:00
Collecting uritemplate>=3.0.0
  Downloading uritemplate-4.2.0-py3-none-any.whl (11 kB)
Collecting jsonschema
  Downloading jsonschema-4.25.1-py3-none-any.whl (90 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 90.0/90.0 KB 253.9 MB/s eta 0:00:00
Collecting termcolor
  Downloading termcolor-3.2.0-py3-none-any.whl (7.7 kB)
Collecting rfc3986<2
  Downloading rfc3986-1.5.0-py2.py3-none-any.whl (31 kB)
Collecting isodate
  Downloading isodate-0.7.2-py3-none-any.whl (22 kB)
Collecting wrapt
  Downloading wrapt-2.0.1-cp310-cp310-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (113 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 113.7/113.7 KB 252.2 MB/s eta 0:00:00
Collecting jsonschema-specifications>=2023.03.6
  Downloading jsonschema_specifications-2025.9.1-py3-none-any.whl (18 kB)
Collecting referencing>=0.28.4
  Downloading referencing-0.37.0-py3-none-any.whl (26 kB)
Collecting rpds-py>=0.7.1
  Downloading rpds_py-0.29.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (392 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 392.7/392.7 KB 309.7 MB/s eta 0:00:00
Collecting six>=1.5
  Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Collecting pyparsing<4,>=2.1.0
  Downloading pyparsing-3.2.5-py3-none-any.whl (113 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 113.9/113.9 KB 269.6 MB/s eta 0:00:00
Building wheels for collected packages: docopt
  Building wheel for docopt (setup.py): started
  Building wheel for docopt (setup.py): finished with status 'done'
  Created wheel for docopt: filename=docopt-0.6.2-py2.py3-none-any.whl size=13723 sha256=bf715b75c9973f8f6b8ca3d0f59cb3eddd4161dff44751dcdbd4f5b8515285c1
  Stored in directory: /tmp/pip-ephem-wheel-cache-5k9fqv81/wheels/fc/ab/d4/5da2067ac95b36618c629a5f93f809425700506f72c9732fac
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
The command '/bin/sh -c pip install --no-cache-dir -r /app/requirements.txt' returned a non-zero code: 2
ERROR
ERROR: build step 0 "gcr.io/cloud-builders/gcb-internal" failed: step exited with non-zero status: 2

-------------------------------------------------------------------------------------------------------------------------------------------------------------

BUILD FAILURE: Build step failure: build step 0 "gcr.io/cloud-builders/gcb-internal" failed: step exited with non-zero status: 2
ERROR: (gcloud.builds.submit) build 9dce7d38-533e-4a5b-a1f4-6fe2d9835494 completed with status "FAILURE"
re_nikitav@cloudshell:~/fastapi_impl_gpu (emr-dgt-autonomous-uctr1-snbx)$ 

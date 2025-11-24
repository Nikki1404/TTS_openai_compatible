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
re_nikitav@cloudshell:~/fastapi_impl_gpu (emr-dgt-autonomous-uctr1-snbx

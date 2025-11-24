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

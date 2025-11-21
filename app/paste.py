{
  "message": {
    "conversationId": "CID-TEST-001",
    "speaker": "agent",
    "transcript": "Hi, this is a test message from sample.json.",
    "agentType": "BOT",

    "hm-conversation-metadata": {
      "agentData": {
        "agentName": "John Doe",
        "experienceYears": 4,
        "qualityScore": 92
      },
      "ccaasData": {
        "check1": true,
        "check2": "verified"
      },
      "intervention": "No escalation needed"
    }
  }
}

docker build -t us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0 .
docker push us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0
us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0


gcloud run deploy hm-outreach-ws \
  --image us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080


curl -X POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
     -H "Content-Type: application/json" \
     -d @sample.json

nbx)$ vim sample.json 
re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ vi sample.json 
re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ curl -X POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
     -H "Content-Type: application/json" \
     -d @sample.json
{"error":"ERROR FOUND AT SAVING TRANSCRIPT: 403 Missing or insufficient permissions."}re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ 
""


gcloud run services describe hm-outreach-ws \
  --region us-central1 \
  --format "value(spec.template.spec.serviceAccountName)"
150916788856-compute@developer.gserviceaccount.com

gcloud projects add-iam-policy-binding emr-dgt-autonomous-uctr1-snbx \
  --member="serviceAccount:150916788856-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding emr-dgt-autonomous-uctr1-snbx \
  --member="serviceAccount:150916788856-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.owner"

gcloud run deploy hm-outreach-ws \
  --image us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080

curl -X POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
     -H "Content-Type: application/json" \
     -d @sample.json



gcloud projects get-iam-policy emr-dgt-autonomous-uctr1-snbx \
  --flatten="bindings[].members" \
  --format='table(bindings.role, bindings.members)' \
  --filter="150916788856-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding --condition=None

gcloud projects add-iam-policy-binding emr-dgt-autonomous-uctr1-snbx \
  --member="serviceAccount:150916788856-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None


gcloud projects add-iam-policy-binding emr-dgt-autonomous-uctr1-snbx \
  --member="serviceAccount:150916788856-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.owner" \
  --condition=None


gcloud projects add-iam-policy-binding emr-dgt-autonomous-uctr1-snbx \
    --member="serviceAccount:150916788856-compute@developer.gserviceaccount.com" \
    --role="roles/datastore.user" \
    --condition=None

gcloud run deploy hm-outreach-ws \
  --image us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080


curl -X POST "https://hm-outreach-ws-150916788856.us-central1.run.app/publish" \
     -H "Content-Type: application/json" \
     -d @sample.json




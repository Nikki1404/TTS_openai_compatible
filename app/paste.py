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

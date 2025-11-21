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


re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ docker push us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0
The push refers to repository [us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws]
5e176d8e75d9: Pushed 
27f6a320d17b: Pushed 
ff290fede8a7: Pushed 
cc7b4081dc6c: Pushed 
e269231b9601: Layer already exists 
9c895a85998d: Layer already exists 
ae5637ef40a1: Layer already exists 
70a290c5e58b: Pushed 
4.0.0: digest: sha256:a1c5d0aab618e7f61c6e8e10513182e9b4d9fc209457d4b8b1e7e871d4cce6b5 size: 1993
re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ gcloud run deploy hm-outreach-ws \
  --image us-central1-docker.pkg.dev/emr-dgt-autonomous-uctr1-snbx/cx-poc/pubsub-via-ws:4.0.0 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
Deploying container to Cloud Run service [hm-outreach-ws] in project [emr-dgt-autonomous-uctr1-snbx] region [us-central1]
Deploying new service...                                                                                                                                    
  Setting IAM Policy...done                                                                                                                                 
  Creating Revision...done                                                                                                                                  
  Routing traffic...done                                                                                                                                    
Done.                                                                                                                                                       
Service [hm-outreach-ws] revision [hm-outreach-ws-00001-297] has been deployed and is serving 100 percent of traffic.
Service URL: https://hm-outreach-ws-150916788856.us-central1.run.app
re_nikitav@cloudshell:~/hm_outreach (emr-dgt-autonomous-uctr1-snbx)$ 

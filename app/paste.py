from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import pubsub_v1, datastore
from typing import List
from dbManage import DBManager
import uvicorn
import os
import asyncio
import json
from datetime import datetime, timezone


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ID="emr-dgt-autonomous-uctr1-snbx"
TOPIC_ID="ws-via-ps-topic"
SUBSCRIPTION_ID="ws-via-ps-topic-sub"
DATABASE_ID = "outreach-cx"

db_manager = DBManager(PROJECT_ID, DATABASE_ID)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

ws_manager = ConnectionManager()

@app.get(path='/get_transcript')
async def getTranscript(
    conversationId: str
):
    if not conversationId:
        return JSONResponse(
            status_code=404,
            content={"response": "'conversationId' is missing in the query params."}
        )

    status_code, response = db_manager.getTranscript(conversationId=conversationId)

    if status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": f"ERROR FOUND AT FETCHING TRANSCRIPT: {response}"}
        )

    return JSONResponse(
        status_code=200,
        content={"response": response}
    )

@app.post(path='/add_transcript')
async def addTranscript(
    request: Request
):
    body = await request.json()

    if not body:
        return JSONResponse(
            status_code=500,
            content={"error": "Invalid Json!"}
        )

    if "message" not in body:
        return JSONResponse(
            status_code=404,
            content={"response": "'message' is missing in the request body."}
        )        

    data = body['message']

    if not isinstance(data, dict):
        return JSONResponse(status_code=500, content={"error": "'message' type must be dictionary."})

    if "conversationId" not in data or data['conversationId']=="":
        return JSONResponse(
            status_code=404,
            content={"response": "'conversationId' is either missing in the request body or is it an empty string."}
        )

    if "speaker" not in data or data['speaker']=="":
        return JSONResponse(
            status_code=404,
            content={"response": "'speaker' is either missing in the request body or is it an empty string."}
        )

    timestamp = datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S +0000')

    transcript_data = {
        "conversationId": data["conversationId"],
        "transcript": data.get("transcript", ""),
        "timestamp": timestamp,
        "speaker": data["speaker"],
        "agentType": data.get("agentType", "NA")
    }

    status_code, response = db_manager.addTranscript(data=transcript_data)

    if status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": f"ERROR FOUND AT SAVING TRANSCRIPT: {response}"}
        )

    return JSONResponse(
        status_code=status_code,
        content={"response": "Transcript saved successfully!"}
    )


def insert_hm_conversation_metadata(conversationId, agentData, ccaasData, intervention):
    try:
        client = datastore.Client(project=PROJECT_ID)
        key = client.key("hm-conversation-metadata")
        entity = datastore.Entity(key=key)

        entity.update({
            "conversationId": conversationId,
            "agentData": agentData,
            "ccaasData": ccaasData,
            "intervention": intervention
        })

        client.put(entity)
        print("Metadata inserted into hm-conversation-metadata")

    except Exception as e:
        print(f"Error inserting metadata: {str(e)}")



@app.post(path='/publish')
async def publishPubSubMessage(
    request: Request,
    attributes: dict = None
):
    body = await request.json()

    if not body:
        return JSONResponse(
            status_code=500,
            content={"error": "Invalid Json!"}
        )
    
    message_str = ""

    if "message" not in body:
        return JSONResponse(
            status_code=404,
            content={"response": "'message' is missing in the request body."}
        )        

    attributes = body['message']

    if not isinstance(attributes, dict):
        return JSONResponse(status_code=500, content={"error": "'attributes' type must be dictionary."})

    # Convert your message to bytes
    data = message_str.encode("utf-8")

    if "conversationId" not in attributes or attributes['conversationId']=="":
        return JSONResponse(
            status_code=404,
            content={"response": "'conversationId' is either missing in the request body or is it an empty string."}
        )

    if "speaker" not in attributes or attributes['speaker']=="":
        return JSONResponse(
            status_code=404,
            content={"response": "'speaker' is either missing in the request body or is it an empty string."}
        )

    timestamp = datetime.now(timezone.utc).strftime('%d/%b/%Y:%H:%M:%S +0000')

    transcript_data = {
        "conversationId": attributes["conversationId"],
        "transcript": attributes.get("transcript", ""),
        "timestamp": timestamp,
        "speaker": attributes["speaker"],
        "agentType": attributes.get("agentType", "NA")
    }

    status_code, response = db_manager.addTranscript(data=transcript_data)

    if status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": f"ERROR FOUND AT SAVING TRANSCRIPT: {response}"}
        )

    try:
        hm_root = attributes.get("HMConversationData", {})
        meta = hm_root.get("metaData", {})

        if meta:
            conversationId_val = attributes.get("conversationId", "")
            agentData_val = meta.get("AgentData", {})
            ccaasData_val = meta.get("CKsData", {})
            intervention_val = meta.get("Intervention", "")

            print("Parsed Metadata:")
            print(json.dumps({
                "conversationId": conversationId_val,
                "agentData": agentData_val,
                "ccaasData": ccaasData_val,
                "intervention": intervention_val
            }, indent=2))

            insert_hm_conversation_metadata(
                conversationId_val,
                agentData_val,
                ccaasData_val,
                intervention_val
            )

    except Exception as e:
        print("Error processing hm-conversation-metadata:", str(e))

    # Optional attributes
    if attributes is None:
        attributes = {}

    # Publish returns a Future
    future = publisher.publish(topic_path, data, **attributes)

    # Offload blocking result() call to thread pool
    loop = asyncio.get_running_loop()
    try:
        message_id = await loop.run_in_executor(None, future.result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return JSONResponse(
        status_code=200,
        content={"id": message_id}
    )

@app.post(path="/", status_code=204)
async def index(request: Request):
    """Receive and parse Pub/Sub messages."""
    print("request: ", request)
    envelope = await request.json()
    print("envelope: ", envelope)
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return JSONResponse(status_code=400, content={"error": str(msg)})

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return JSONResponse(status_code=400, content={"error": str(msg)})

    pubsub_message = envelope["message"]

    message = {}
    if isinstance(pubsub_message, dict) and "attributes" in pubsub_message:
        message = pubsub_message["attributes"]

    print(f"Received message in dictionary format: {message}, {type(message)}!")

    await ws_manager.broadcast(message)
    
    # return JSONResponse(status_code=204, content={"response": "Message received successfully!"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # await manager.broadcast(f"Client #{client_id} joined the chat")
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        print("Websocker is disconnected and stopped listening pub-sub messages.")
        # await manager.broadcast("Connection Ended!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

{
  "message": {
    "conversationId": "CID-12345",
    "speaker": "agent",
    "transcript": "Hello, this is a test transcript.",
    "agentType": "BOT",

    "HMConversationData": {
      "metaData": {
        "AgentData": {
          "agentName": "John Doe",
          "agentScore": 92,
          "callSummary": "customer asked about refund"
        },
        "CKsData": {
          "ck1": true,
          "ck2": "completed-id-check"
        },
        "Intervention": "Escalation needed"
      }
    }
  }
}



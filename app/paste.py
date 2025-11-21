from google.cloud import datastore
from datetime import datetime

class DBManager():
    def __init__(self,
                 PROJECT_ID: str,
                 DATABASE_ID: str
                 ):
        self.client = datastore.Client(project=PROJECT_ID, database=DATABASE_ID)

    def addTranscript(
            self,
            data: dict,
            kind = "Transcript"
    ):
        try:
            key = self.client.key(kind)
            entity = datastore.Entity(key=key)
            entity.update(data)
        
            # Save entity to Datastore
            self.client.put(entity)
            return 200, "success"
        except Exception as e:
            print("Error in adding transcript: ", e)
            return 500, str(e)

    def __parse_timestamp(self, entry):
        return datetime.strptime(entry["timestamp"], "%d/%b/%Y:%H:%M:%S %z")

    def getTranscript(
            self,
            conversationId: str,
            kind = "Transcript"
    ):        

        try:
            query = self.client.query(kind=kind)
            query.add_filter('conversationId', '=', conversationId)
            entities = list(query.fetch())
            entities = [dict(x) for x in entities]
            print("entities: ", entities)

            entities = sorted(entities, key=self.__parse_timestamp)
            return 200, entities
        
        except Exception as e:
            print("Error in fetching transcript: ", e)
            return 500, str(e)

    # =====================================================================
    # NEW METHOD REQUESTED BY KUNAL
    # =====================================================================
    def addHMConversationMetadata(
            self,
            conversationId,
            agentData,
            ccaasData,
            intervention,
            kind="hm-conversation-metadata"
    ):
        """
        Inserts conversation metadata into Datastore kind: hm-conversation-metadata
        """
        try:
            key = self.client.key(kind)
            entity = datastore.Entity(key=key)

            entity.update({
                "conversationId": conversationId,
                "agentData": agentData,
                "ccaasData": ccaasData,
                "intervention": intervention
            })

            self.client.put(entity)
            print("Saved into hm-conversation-metadata successfully")

            return 200, "success"

        except Exception as e:
            print("Error in inserting metadata:", str(e))
            return 500, str(e)

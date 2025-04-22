import autogen
from database.pgvector import pgvector_client
from integrations.bedrock import bedrock_client
from utils.logging import logger

class RAGAgent:
    def __init__(self):
        self.proxy = autogen.RetrieveUserProxyAgent(
            name="RAGProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "qa",
                "docs_path": [],
                "vector_db": "pgvector",
                "collection_name": "knowledge_base1",
                "db_config": {
                    "connection_string": f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
                },
                "embedding_function": pgvector_client.embedder.encode,
                "get_or_create": True
            }
        )
        self.assistant = autogen.AssistantAgent(
            name="RAGAssistant",
            system_message="You answer queries using retrieved documents.",
            llm_config={
                "model": "bedrock",
                "client": bedrock_client
            }
        )

    async def process_query(self, message: str, collection: str):
        try:
            self.proxy.retrieve_config["collection_name"] = collection
            documents = await pgvector_client.query(message, collection)
            context = "\n".join(documents)
            prompt = f"Context:\n{context}\n\nQuery:\n{message}"
            response = await bedrock_client.invoke_model(prompt)
            return response
        except Exception as e:
            logger.error({"error": str(e), "collection": collection})
            raise
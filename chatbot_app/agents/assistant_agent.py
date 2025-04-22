import autogen
from integrations.bedrock import bedrock_client
from utils.logging import logger

class AssistantAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="Assistant",
            system_message="You are a coordinator that directs queries to the appropriate agent (RAG, SQL, GraphQL).",
            llm_config={
                "model": "bedrock",
                "client": bedrock_client
            }
        )

    async def process_query(self, message: str, user_id: str, session_id: str, rag_agent, sql_agent, graphql_agent):
        try:
            # Simple intent detection (can be enhanced with NLP)
            if any(keyword in message.lower() for keyword in ["sql", "database", "query data"]):
                return await sql_agent.process_query(message)
            elif any(keyword in message.lower() for keyword in ["graphql", "api"]):
                return await graphql_agent.process_query(message)
            else:
                return await rag_agent.process_query(message, "knowledge_base1")
        except Exception as e:
            logger.error({"error": str(e), "user_id": user_id, "session_id": session_id})
            return "An error occurred. Please try again."
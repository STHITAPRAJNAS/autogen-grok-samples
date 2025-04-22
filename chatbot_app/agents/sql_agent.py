from integrations.bedrock import bedrock_client
from integrations.databricks import databricks_client
from utils.logging import logger

class SQLAgent:
    async def process_query(self, message: str):
        try:
            # Generate SQL query using Bedrock
            prompt = f"Convert this natural language query to SQL: {message}"
            sql_query = await bedrock_client.invoke_model(prompt)
            # Execute query on Databricks
            results = await databricks_client.execute_query(sql_query)
            return results
        except Exception as e:
            logger.error({"error": str(e), "query": message})
            raise
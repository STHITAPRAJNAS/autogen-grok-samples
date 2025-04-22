from integrations.bedrock import bedrock_client
from integrations.graphql import graphql_client
from utils.logging import logger

class GraphQLAgent:
    async def process_query(self, message: str):
        try:
            # Discover schema if not already done
            if not graphql_client.schema:
                await graphql_client.discover_schema()
            
            # Generate GraphQL query using Bedrock
            prompt = f"Using the following schema:\n{graphql_client.schema}\nConvert this query to GraphQL: {message}"
            graphql_query = await bedrock_client.invoke_model(prompt)
            
            # Execute GraphQL query
            result = await graphql_client.execute_query(graphql_query)
            return result
        except Exception as e:
            logger.error({"error": str(e), "query": message})
            raise
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import get_introspection_query
from config.settings import settings
from utils.logging import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class GraphQLClient:
    def __init__(self):
        self.transport = AIOHTTPTransport(url=settings.GRAPHQL_ENDPOINT)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
        self.schema = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def discover_schema(self):
        try:
            result = await self.client.execute_async(gql(get_introspection_query()))
            self.schema = result
            return self.schema
        except Exception as e:
            logger.error({"error": str(e)})
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def execute_query(self, query: str):
        try:
            result = await self.client.execute_async(gql(query))
            return result
        except Exception as e:
            logger.error({"error": str(e), "query": query})
            raise

graphql_client = GraphQLClient()
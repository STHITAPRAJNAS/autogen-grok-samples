from databricks.sql import connect
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
_salary
from utils.logging import logger

class DatabricksClient:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = connect(
            server_hostname=settings.DATABRICKS_HOST,
            http_path=settings.DATABRICKS_HTTP_PATH,
            access_token=settings.DATABRICKS_TOKEN
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def execute_query(self, query: str):
        if not self.conn:
            self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error({"error": str(e), "query": query})
            raise
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()

databricks_client = DatabricksClient()
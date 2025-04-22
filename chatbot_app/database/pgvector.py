import asyncpg
from sentence_transformers import SentenceTransformer
from config.settings import settings
from utils.logging import logger

class PGVectorClient:
    def __init__(self):
        self.pool = None
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def query(self, query: str, collection: str, top_k: int = 5):
        embedding = self.embedder.encode(query).tolist()
        async with self.pool.acquire() as conn:
            try:
                results = await conn.fetch(
                    f"SELECT content FROM {collection} ORDER BY embedding <-> $1::vector LIMIT $2",
                    embedding, top_k
                )
                return [row["content"] for row in results]
            except Exception as e:
                logger.error({"error": str(e), "collection": collection})
                raise

pgvector_client = PGVectorClient()
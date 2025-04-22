import asyncpg
import json
from config.settings import settings
from utils.logging import logger

class ConversationStore:
    def __init__(self):
        self.pool = None

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

    async def store_conversation(self, user_id: str, session_id: str, message: dict):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO conversations (user_id, session_id, message) VALUES ($1, $2, $3)",
                    user_id, session_id, json.dumps(message)
                )
            except Exception as e:
                logger.error({"error": str(e), "user_id": user_id, "session_id": session_id})
                raise

    async def load_conversation(self, user_id: str, session_id: str):
        async with self.pool.acquire() as conn:
            try:
                results = await conn.fetch(
                    "SELECT message FROM conversations WHERE user_id = $1 AND session_id = $2 ORDER BY timestamp",
                    user_id, session_id
                )
                return [json.loads(row["message"]) for row in results]
            except Exception as e:
                logger.error({"error": str(e), "user_id": user_id, "session_id": session_id})
                raise

conversation_store = ConversationStore()
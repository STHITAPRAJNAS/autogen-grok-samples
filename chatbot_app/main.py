from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import anyio
from anyio.lowlevel import RunVar
from anyio import create_task_group
from database.pgvector import pgvector_client
from database.conversation import conversation_store
from agents.assistant_agent import AssistantAgent
from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from agents.graphql_agent import GraphQLAgent
from utils.logging import logger
from utils.metrics import request_counter, response_time_histogram
from prometheus_client import start_http_server
import time

app = FastAPI()

class UserInput(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.on_event("startup")
async def startup_event():
    RunVar("_default_thread_limiter").set(anyio.CapacityLimiter(10))
    await pgvector_client.init_pool()
    await conversation_store.init_pool()
    start_http_server(8001)  # Prometheus metrics
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    await pgvector_client.close_pool()
    await conversation_store.close_pool()
    databricks_client.close()
    logger.info("Application shutdown")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async with create_task_group() as tg:
            while True:
                data = await websocket.receive_json()
                user_input = UserInput(**data)
                request_counter.labels(endpoint="websocket").inc()
                
                async def process_and_send():
                    with response_time_histogram.labels(endpoint="websocket").time():
                        response = await process_query(user_input)
                        await websocket.send_json({"response": response})
                
                tg.start_soon(process_and_send)
    except Exception as e:
        logger.error({"error": str(e)})
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@app.post("/chat")
async def chat_endpoint(user_input: UserInput):
    request_counter.labels(endpoint="rest").inc()
    with response_time_histogram.labels(endpoint="rest").time():
        response = await process_query(user_input)
    return {"response": response}

async def process_query(user_input: UserInput):
    try:
        # Load conversation history
        history = await conversation_store.load_conversation(user_input.user_id, user_input.session_id)
        
        # Initialize agents
        assistant = AssistantAgent()
        rag_agent = RAGAgent()
        sql_agent = SQLAgent()
        graphql_agent = GraphQLAgent()
        
        # Process query
        response = await assistant.process_query(
            user_input.message,
            user_input.user_id,
            user_input.session_id,
            rag_agent,
            sql_agent,
            graphql_agent
        )
        
        # Store conversation
        await conversation_store.store_conversation(
            user_input.user_id,
            user_input.session_id,
            {"user": user_input.message, "assistant": response}
        )
        
        return response
    except Exception as e:
        logger.error({"error": str(e), "user_id": user_input.user_id, "session_id": user_input.session_id})
        return "An error occurred. Please try again."

# Run with Gunicorn
# gunicorn -w $((2 * $(getconf _NPROCESSORS_ONLN) + 1)) --timeout 12600 -k uvicorn.workers.UvicornWorker main:app
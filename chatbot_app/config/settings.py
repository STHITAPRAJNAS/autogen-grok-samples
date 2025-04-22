import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_REGION = os.getenv("AWS_REGION")
    BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
    DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
    GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
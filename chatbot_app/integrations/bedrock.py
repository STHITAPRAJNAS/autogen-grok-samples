import boto3
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from utils.logging import logger

class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def invoke_model(self, prompt: str):
        try:
            response = self.client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": 1000,
                    "temperature": 0.7
                })
            )
            result = json.loads(response["body"].read())
            return result.get("completion", "")
        except Exception as e:
            logger.error({"error": str(e), "model_id": settings.BEDROCK_MODEL_ID})
            raise

bedrock_client = BedrockClient()
import logging
import openai
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)

OPENAI_MODEL_VERSION = "gpt-4o-mini"


class OpenAIConnector:
    def __init__(self, api_key):
        logger.info("Connecting to OpenAI...")
        self.client = openai.Client(api_key=api_key)
        logger.info("Connected to OpenAI successfully.")

    def create_completion(self, messages: list[ChatCompletionMessageParam]):
        logger.info("Creating chat completion from OpenAI...")
        return self.client.chat.completions.create(
            model=OPENAI_MODEL_VERSION,
            messages=messages,
            stream=True,
        )

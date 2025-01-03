import logging
import openai

logger = logging.getLogger(__name__)


class OpenAIConnector:
    def __init__(self, api_key):
        logger.info("Connecting to OpenAI...")
        self.client = openai.Client(api_key=api_key)
        logger.info("Connected to OpenAI successfully.")

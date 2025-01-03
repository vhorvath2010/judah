import logging
import os

from judah.openai_connector import OpenAIConnector

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info("Connecting to OpenAI...")
openai = OpenAIConnector(api_key=os.environ.get("OPENAI_API_KEY"))
logger.info("Connected to OpenAI successfully!")

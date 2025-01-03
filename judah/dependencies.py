import os

from judah.openai_connector import OpenAIConnector

openai_connector = OpenAIConnector(api_key=os.environ.get("OPENAI_API_KEY"))

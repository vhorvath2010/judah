import os

from judah.openai_connector import OpenAIConnector

openai = OpenAIConnector(api_key=os.environ.get("OPENAI_API_KEY"))

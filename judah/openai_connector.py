import openai


class OpenAIConnector:
    def __init__(self, api_key):
        self.client = openai.Client(api_key=api_key)

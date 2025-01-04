import os

from judah.audio.audio_input_engine import AudioInputEngine
from judah.conversation_runner import ConversationRunner
from judah.openai_connector import OpenAIConnector

openai_connector = OpenAIConnector(api_key=os.environ.get("OPENAI_API_KEY"))
audio_input_engine = AudioInputEngine()
conversation_runner = ConversationRunner(openai_connector=openai_connector, audio_input_engine=audio_input_engine)

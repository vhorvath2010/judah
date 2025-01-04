import os

from judah.audio.audio_input_engine import AudioInputEngine
from judah.conversaion_manager import ConversationManager
from judah.openai_connector import OpenAIConnector

openai_connector = OpenAIConnector(api_key=os.environ.get("OPENAI_API_KEY"))
conversation_manager = ConversationManager(openai_connector=openai_connector)

audio_input_engine = AudioInputEngine()

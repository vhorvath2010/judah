import os

from judah.audio.audio_input_engine import AudioInputEngine
from judah.conversation_runner import ConversationRunner
from judah.functions.end_conversation import EndConversationFunction
from judah.functions.function_invoker import FunctionInvoker
from judah.openai_connector import OpenAIConnector

end_conversation_function = EndConversationFunction()
available_functions = [end_conversation_function]
function_invoker = FunctionInvoker(available_functions=available_functions)

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("You must set the OPENAI_API_KEY environment variable!")
openai_connector = OpenAIConnector(
    api_key=openai_api_key,
    available_tools=[function.get_description() for function in available_functions],
)

audio_input_engine = AudioInputEngine()

conversation_runner = ConversationRunner(
    openai_connector=openai_connector,
    audio_input_engine=audio_input_engine,
    function_invoker=function_invoker,
)

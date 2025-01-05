import os

from judah.audio.audio_input_engine import AudioInputEngine
from judah.audio.audio_output_engine import AudioOutputEngine
from judah.connectors.todoist_connector import TodoistConnector
from judah.conversation.conversation_runner import ConversationRunner
from judah.functions.complete_todo_item import CompleteTodoItemFunction
from judah.functions.end_conversation import EndConversationFunction
from judah.functions.function_invoker import FunctionInvoker
from judah.connectors.openai_connector import OpenAIConnector
from judah.functions.get_todo_items import GetTodoItemsFunction
from judah.functions.openai_function import OpenAIFunction

end_conversation_function = EndConversationFunction()
available_functions: list[OpenAIFunction] = [end_conversation_function]

if os.environ.get("TODOIST_API_KEY") is not None:
    todoist_connector = TodoistConnector(api_key=os.environ.get("TODOIST_API_KEY"))
    get_todo_items_function = GetTodoItemsFunction(todoist_connector=todoist_connector)
    complete_todo_item_function = CompleteTodoItemFunction(
        todoist_connector=todoist_connector
    )
    available_functions.extend([get_todo_items_function, complete_todo_item_function])

function_invoker = FunctionInvoker(available_functions=available_functions)

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("You must set the OPENAI_API_KEY environment variable!")
openai_connector = OpenAIConnector(
    api_key=openai_api_key,
    available_tools=[function.get_description() for function in available_functions],
)

audio_input_engine = AudioInputEngine()
audio_output_engine = AudioOutputEngine()

conversation_runner = ConversationRunner(
    openai_connector=openai_connector,
    audio_input_engine=audio_input_engine,
    audio_output_engine=audio_output_engine,
    function_invoker=function_invoker,
)

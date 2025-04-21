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
from judah.connectors.mcp_connector import MCPConnector
from judah.functions.list_mcp_resources import ListMCPResourcesFunction
from judah.functions.list_mcp_tools import ListMCPToolsFunction
from judah.functions.call_mcp_tool import CallMCPToolFunction

end_conversation_function = EndConversationFunction()
available_functions: list[OpenAIFunction] = [end_conversation_function]

if os.environ.get("TODOIST_API_KEY") is not None:
    todoist_connector = TodoistConnector(api_key=os.environ.get("TODOIST_API_KEY"))
    get_todo_items_function = GetTodoItemsFunction(todoist_connector=todoist_connector)
    complete_todo_item_function = CompleteTodoItemFunction(
        todoist_connector=todoist_connector
    )
    available_functions.extend([get_todo_items_function, complete_todo_item_function])

mcp_args = os.environ.get("MCP_ARGS", "").split() if os.environ.get("MCP_ARGS") else []
if os.environ.get("MCP_ENV"):
    mcp_env = {
        kv.split("=", 1)[0]: kv.split("=", 1)[1]
        for kv in os.environ["MCP_ENV"].split(";")
        if "=" in kv
    }
else:
    mcp_env = None
mcp_connector = MCPConnector(command=mcp_command, args=mcp_args, env=mcp_env)
list_resources_fn = ListMCPResourcesFunction(mcp_connector=mcp_connector)
list_tools_fn = ListMCPToolsFunction(mcp_connector=mcp_connector)
call_tool_fn = CallMCPToolFunction(mcp_connector=mcp_connector)
available_functions.extend([list_resources_fn, list_tools_fn, call_tool_fn])

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

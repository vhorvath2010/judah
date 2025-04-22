import os

from judah.audio.audio_input_engine import AudioInputEngine
from judah.audio.audio_output_engine import AudioOutputEngine
from judah.conversation.conversation_runner import ConversationRunner
from judah.functions.end_conversation import EndConversationFunction
from judah.functions.function_invoker import FunctionInvoker
from judah.connectors.openai_connector import OpenAIConnector
from judah.functions.tool import Tool
from judah.connectors.mcp_connector import MCPConnector, ServerConfig
from openai.types.chat import ChatCompletionToolParam

end_conversation_function = EndConversationFunction()
available_functions: list[Tool] = [end_conversation_function]
mcp_connector = MCPConnector(
    configs=[
        ServerConfig(name="default", command="mcp", args=[], env=None),
        # Add additional MCP servers here
    ]
)
mcp_tool_defs: list[ChatCompletionToolParam] = (
    mcp_connector.get_openai_function_descriptions()
)
available_openai_tools: list[ChatCompletionToolParam] = [
    *[fn.get_openai_description() for fn in available_functions],
    *mcp_tool_defs,
]

function_invoker = FunctionInvoker(available_functions=available_functions)

openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("You must set the OPENAI_API_KEY environment variable!")
openai_connector = OpenAIConnector(
    api_key=openai_api_key,
    available_tools=available_openai_tools,
)

audio_input_engine = AudioInputEngine()
audio_output_engine = AudioOutputEngine()

conversation_runner = ConversationRunner(
    openai_connector=openai_connector,
    audio_input_engine=audio_input_engine,
    audio_output_engine=audio_output_engine,
    function_invoker=function_invoker,
)

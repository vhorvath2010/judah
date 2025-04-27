import os

from mcp import StdioServerParameters

from judah.audio.audio_input_engine import AudioInputEngine
from judah.audio.audio_output_engine import AudioOutputEngine
from judah.connectors.mcp_connector import MCPConnector
from judah.conversation.conversation_runner import ConversationRunner
from judah.functions.end_conversation import EndConversationFunction
from judah.functions.function_invoker import FunctionInvoker
from judah.connectors.openai_connector import OpenAIConnector
from judah.functions.openai_function import OpenAIFunction

end_conversation_function = EndConversationFunction()
available_functions: list[OpenAIFunction] = [end_conversation_function]
mcp_connector = MCPConnector()
if os.environ.get("TODOIST_API_KEY") is not None:
    todoist_mcp_params = StdioServerParameters(
        command="npx",
        args=["-y", "@abhiz123/todoist-mcp-server"],
        env={"TODOIST_API_TOKEN": os.environ.get("TODOIST_API_KEY")},
    )
    mcp_connector.connect_to_server(todoist_mcp_params)
if os.environ.get("GITHUB_ACCESS_TOKEN") is not None:
    github_mcp_params = StdioServerParameters(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server",
        ],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_ACCESS_TOKEN")},
    )
    mcp_connector.connect_to_server(github_mcp_params)
print("setting up fetch")
fetch_mcp_params = StdioServerParameters(
    command="docker", args=["run", "-i", "--rm", "mcp/fetch"]
)
print("setting up fetch2")

mcp_connector.connect_to_server(fetch_mcp_params)
print("setting up fetch done")

available_functions.extend(mcp_connector.get_functions())
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

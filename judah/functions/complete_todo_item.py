from openai.types.chat import ChatCompletionToolParam

from judah.connectors.todoist_connector import TodoistConnector
from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction


class CompleteTodoItemFunction(OpenAIFunction):
    def __init__(self, todoist_connector: TodoistConnector):
        self._todoist_connector = todoist_connector

    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "complete_todo_item",
                "description": "Mark a todo item as done in Todoist",
                "parameters": {
                    "type": "object",
                    "properties": {"task_id": {"type": "string"}},
                    "required": ["task_id"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    def invoke(self, arguments: dict) -> FunctionResult:
        success = self._todoist_connector.complete_task(
            task_id=str(arguments.get("task_id"))
        )
        return FunctionResult(context=f"Success: {success}")

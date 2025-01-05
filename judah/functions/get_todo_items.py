from openai.types.chat import ChatCompletionToolParam

from judah.connectors.todoist_connector import TodoistConnector
from judah.functions.function_result import FunctionResult
from judah.functions.openai_function import OpenAIFunction


class GetTodoItemsFunction(OpenAIFunction):
    def __init__(self, todoist_connector: TodoistConnector):
        self._todoist_connector = todoist_connector

    @staticmethod
    def get_description() -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": "get_todo_items",
                "description": "Get the user's todo items from Todoist",
            },
        }

    def invoke(self) -> FunctionResult:
        # TODO: implement function calling args
        tasks = self._todoist_connector.get_tasks(task_filter="today")
        return FunctionResult(context=f"Tasks: {tasks}")

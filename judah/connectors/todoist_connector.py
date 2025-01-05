from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task


class TodoistConnector:
    def __init__(self, api_key):
        self._todoist = TodoistAPI(api_key)

    def get_tasks(self, task_filter) -> list[Task]:
        return self._todoist.get_tasks(filter=task_filter)

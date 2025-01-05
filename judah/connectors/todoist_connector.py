from todoist_api_python.api import TodoistAPI


class TodoistConnector:
    def __init__(self, api_key):
        self._todoist = TodoistAPI(api_key)
        print(self.get_tasks("today"))

    def get_tasks(self, task_filter):
        return self._todoist.get_tasks(filter=task_filter)

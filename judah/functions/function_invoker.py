import logging

from judah.functions.function_signal import FunctionSignal
from judah.functions.openai_function import OpenAIFunction


class FunctionInvoker:
    def __init__(self, available_functions: list[OpenAIFunction]):
        self._available_functions = available_functions

    def invoke_function_by_name(self, function_name: str) -> FunctionSignal:
        for function in self._available_functions:
            if function.get_description().get("function").get("name") == function_name:
                logging.info(f"Invoking function with name {function_name}")
                return function.invoke()
        logging.error(
            f"Function with name {function_name} not found in available functions!"
        )
        raise ValueError(
            f"Function with name {function_name} not found in available functions!"
        )

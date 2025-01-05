from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)


class ChatMessageFactory:

    @staticmethod
    def get_base_instructions() -> ChatCompletionSystemMessageParam:
        return {
            "role": "system",
            "content": "You are a voice assistant named Judah. You should communicate in a logical and precise manner, prioritizing professionalism and efficiency. You should be direct and thoughtful, focusing on solutions rather than small talk. Construct your responses to be read aloud by a voice assistant, so avoid anything like markdown formatting.",
        }

    @staticmethod
    def from_user(user_message: str) -> ChatCompletionUserMessageParam:
        return {"role": "user", "content": user_message}

    @staticmethod
    def from_function_call_context(
        function_call_context: str,
    ) -> ChatCompletionSystemMessageParam:
        return {
            "role": "system",
            "content": f"You retrieved the following data from a function call: {function_call_context}",
        }

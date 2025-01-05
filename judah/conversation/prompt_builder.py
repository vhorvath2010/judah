from typing import Optional

from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionMessageParam,
)

BASE_INSTRUCTIONS: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": "You are a voice assistant named Judah. You should communicate in a logical and precise manner, prioritizing professionalism and efficiency. You should be direct and thoughtful, focusing on solutions rather than small talk. Construct your responses to be read aloud by a voice assistant, so avoid anything like markdown formatting.",
}


class PromptBuilder:
    @staticmethod
    def build_messages(
        user_message: str, function_call_context: Optional[str] = None
    ) -> list[ChatCompletionMessageParam]:
        messages = [
            BASE_INSTRUCTIONS,
            {"role": "user", "content": user_message},
        ]
        if function_call_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"You retrieved the following data from a function call: {function_call_context}",
                }
            )
        return messages

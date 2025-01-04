import logging
import warnings

import speech_recognition as sr

from judah.dependencies import conversation_runner, audio_input_engine

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore", category=FutureWarning)  # Ignore annoying PyTorch warning from Whisper


def get_next_conversation_starter() -> str:
    while True:
        try:
            result = audio_input_engine.listen_for_user_message()
            if "judah" in result.lower():
                return result
        except sr.UnknownValueError:
            print("Whisper could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Whisper; {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == '__main__':
    while True:
        print('Say a phrase including the "Judah" wake word to start a new conversation!')
        user_message = get_next_conversation_starter()
        conversation_runner.run_conversation_to_completion(starting_user_message=user_message)

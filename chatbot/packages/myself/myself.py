import os
import time

from dotenv import load_dotenv
# from fancify_text import bold, italic
from openai.error import ServiceUnavailableError

from config import CHAT_HISTORIES
from chatbot.user import User
from chatbot.sharedinstances import send_api

from .core.dependencies import chatgpt
from chatbot.packages.common.common import block_successive_actions

load_dotenv()


@block_successive_actions
def fallback(recipient_id):
    user = User(recipient_id)
    send_api.send_text_message("Désolé, je ne comprends pas ce que vous dites.", recipient_id)


@block_successive_actions
def respond_to_user(prompt, recipient_id):
    user = User(recipient_id)

    chatbot = chatgpt.Chatbot(api_key=os.getenv("OPENAI_API_TOKEN"))
    try:
        chatbot.load_chat_history(f"{CHAT_HISTORIES}/{recipient_id}.json")
    except FileNotFoundError:
        print(f"Chat history for user {recipient_id} doesn't exist yet.")

    retries = 0
    while retries < 5:
        try:
            response = chatbot.ask(prompt)
        except ServiceUnavailableError:
            print("Failed to send request to api, retrying...")
            time.sleep(10)
        else:
            break

    send_api.send_text_message(response["choices"][0]["text"], recipient_id)

    chatbot.dump_chat_history(f"{CHAT_HISTORIES}/{recipient_id}.json")

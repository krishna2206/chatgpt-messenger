import os

from dotenv import load_dotenv
# from fancify_text import bold, italic
from revChatGPT.Official import Chatbot

from chatbot.user import User
from chatbot.sharedinstances import send_api

from chatbot.packages.common.common import block_successive_actions

load_dotenv()

chatbot = Chatbot(api_key=os.getenv("OPENAI_API_TOKEN"))


@block_successive_actions
def fallback(recipient_id):
    user = User(recipient_id)
    send_api.send_text_message("I'm sorry, I don't understand", recipient_id)


@block_successive_actions
def respond_to_user(prompt, recipient_id):
    user = User(recipient_id)

    chatbot.load_conversation_history()
    response = chatbot.ask(prompt)

    send_api.send_text_message(response["choices"][0]["text"], recipient_id)
    chatbot.dump_conversation_history()

from revChatGPT.V1 import Chatbot

from config import CHATGPT_MODE, ADMIN_USER_ID

from chatbot.user import User
from chatbot.sharedinstances import send_api

from .core.logic import load_config, divide_text
from .core.chatgptusers_model import ChatGPTUserModel
from chatbot.packages.common.common import block_successive_actions, safe_execute_action

chatgptuser_model = ChatGPTUserModel()


@block_successive_actions
def fallback(recipient_id):
    user = User(recipient_id)

    send_api.send_text_message(
        "Désolé, je ne comprends pas ce que vous dites.",
        recipient_id)


@safe_execute_action
@block_successive_actions
def respond_to_user(prompt, recipient_id):
    user = User(recipient_id)

    try:
        chatgpt_config = load_config()
    except FileNotFoundError:
        if recipient_id == ADMIN_USER_ID:
            send_api.send_text_message(
                "⚠️ Le fichier de configuration du chatbot est introuvable.",
                recipient_id)    
        else:
            send_api.send_text_message(
                "⚠️ Le fichier de configuration du chatbot est introuvable.\n" +
                "Veuillez contacter l'administrateur du bot. 👇\n\n" +
                "https://web.facebook.com/fitiavana.leonheart",
                recipient_id)
    else:
        send_api.send_text_message(
            "⏳ Un instant, je vous réponds...",
            recipient_id)

        if CHATGPT_MODE == "V1":
            chatgpt_user = chatgptuser_model.get_user(recipient_id)
            conversation_id = None
            parent_id = None

            if chatgpt_user is None:
                chatgptuser_model.insert_user(recipient_id)
            else:
                conversation_id = chatgpt_user["conversation_id"]
                parent_id = chatgpt_user["parent_id"]

            conversation_id, parent_id = __V1_respond_to_user(
                chatgpt_config, conversation_id, parent_id, prompt, recipient_id)
            chatgptuser_model.update_user(
                recipient_id, conversation_id=conversation_id, parent_id=parent_id)

        else:
            send_api.send_text_message(
                "Mode de chatbot non reconnu 😵",
                recipient_id)


def __V1_respond_to_user(
    config: dict, conversation_id: str,
    parent_id: str, prompt: str, recipient_id: str
) -> tuple:
    chatbot = Chatbot(
        config=config,
        conversation_id=conversation_id,
        parent_id=parent_id)

    message = ""
    for data in chatbot.ask(prompt):
        message = data["message"]
        conversation_id = data["conversation_id"]
        parent_id = data["parent_id"]

    if len(message) > 2000:
        segments = divide_text(message)
        for segment in segments:
            send_api.send_text_message(
                segment,
                recipient_id)
    else:
        send_api.send_text_message(
            message,
            recipient_id)

    return conversation_id, parent_id

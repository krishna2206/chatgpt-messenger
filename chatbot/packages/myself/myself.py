from revChatGPT.V1 import Chatbot, Error

from config import CHATGPT_MODE, ADMIN_USER_ID

from chatbot.user import User
from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components

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


def welcome_message(recipient_id):
    send_api.send_text_message(
        "Bienvenue ! Je suis ChatGPT, un modèle de langage développé par OpenAI. Je suis conçu pour comprendre et générer du langage naturel, ce qui me permet de communiquer avec les utilisateurs comme vous. Mon but est d'aider les gens en répondant à leurs questions et en fournissant des informations précises et utiles. Si vous avez des questions, n'hésitez pas à me demander!",
        recipient_id
    )


def ask_clear_conversation_context(recipient_id: str):
    quickreplies = msgr_api_components.QuickReplies()

    yes_quickrep = msgr_api_components.QuickReply(
        title="✅ Oui",
        payload=Payload(
            target_action="clear_conversation_context",
            clear="true").get_content()
    )
    quickreplies.add_quick_reply(yes_quickrep.get_content())

    no_quickrep = msgr_api_components.QuickReply(
        title="❌ Non",
        payload=Payload(
            target_action="clear_conversation_context",
            clear="false").get_content()
    )
    quickreplies.add_quick_reply(no_quickrep.get_content())

    send_api.send_quick_replies(
        "⚠️ Voulez-vous vraiment effacer le contexte de la conversation ? (Le chatbot va oublier ce qu'il a appris)",
        quickreplies.get_content(),
        recipient_id)


def clear_conversation_context(clear: str, recipient_id: str):
    if clear == "true":
        chatgptuser_model.delete_user(recipient_id)

        send_api.send_text_message(
            "✅ Le contexte de la conversation a été effacé.",
            recipient_id)
    else:
        send_api.send_text_message(
            "⛔ Le contexte de la conversation n'a pas été effacé.",
            recipient_id)


@safe_execute_action
@block_successive_actions
def respond_to_user(prompt: str, recipient_id: str):
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

            if (conversation_id is not None) and (parent_id is not None):
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
    conversation_id = None
    parent_id = None
    try:
        for data in chatbot.ask(prompt):
            message = data["message"]
            conversation_id = data["conversation_id"]
            parent_id = data["parent_id"]
    except Error as error:
        try:
            error_code = int(error.code)
        except ValueError:
            error_code = 524

        if error_code == 524:
            send_api.send_text_message(
                "⚠️ Le serveur est actuellement surchargé, veuillez réessayer plus tard.",
                recipient_id)
        else:
            send_api.send_text_message(
                f"⚠️ Une erreur est survenue ! Code d'erreur : {error_code}",
                recipient_id)
    else:
        if message == "":
            send_api.send_text_message(
                "⚠️ Trop de requêtes en 1 heure, veuillez réessayer plus tard.",
                recipient_id)

        else:
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

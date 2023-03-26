import traceback
import asyncio
from datetime import datetime

from revChatGPT.typings import Error
from revChatGPT.V1 import Chatbot as ChatbotV1
from revChatGPT.V3 import Chatbot as ChatbotV3
from EdgeGPT import Chatbot as EdgeGPTChatbot, ConversationStyle

from config import ADMIN_USER_ID, FB_ACCESS_TOKEN

from chatbot.user import User
from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components

from .core.logic import load_config, divide_text
from .core.dependencies.pageusers import GraphApiError, PageUser
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
    send_api.send_text_message(
        "⛔ Vous n'êtes pas autorisé à utiliser cette commande.",
        recipient_id
    )

    # quickreplies = msgr_api_components.QuickReplies()

    # yes_quickrep = msgr_api_components.QuickReply(
    #     title="✅ Oui",
    #     payload=Payload(
    #         target_action="clear_conversation_context",
    #         clear="true").get_content()
    # )
    # quickreplies.add_quick_reply(yes_quickrep.get_content())

    # no_quickrep = msgr_api_components.QuickReply(
    #     title="❌ Non",
    #     payload=Payload(
    #         target_action="clear_conversation_context",
    #         clear="false").get_content()
    # )
    # quickreplies.add_quick_reply(no_quickrep.get_content())

    # send_api.send_quick_replies(
    #     "⚠️ Voulez-vous vraiment effacer le contexte de la conversation ? (Le chatbot va oublier ce qu'il a appris)",
    #     quickreplies.get_content(),
    #     recipient_id)


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
        # ? Use EdgeGPT credentials for the public config
        edge_gpt_config = load_config()
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
        chatgpt_user = chatgptuser_model.get_user(recipient_id)
        email = None
        password = None
        openai_key = None
        conversation_id = None
        parent_id = None
        daily_free_messages = 10
        last_message_date = datetime.today().timestamp()

        if chatgpt_user is None:
            chatgptuser_model.insert_user(recipient_id)
        else:
            conversation_id = chatgpt_user["conversation_id"]
            parent_id = chatgpt_user["parent_id"]
            email = chatgpt_user["email"]
            password = chatgpt_user["password"]
            openai_key = chatgpt_user["openai_key"]
            daily_free_messages = chatgpt_user["daily_free_messages"]
            last_message_date = chatgpt_user["last_message_date"]

        # ? V1
        if (email is not None) and (password is not None):
            conversation_id, parent_id = __V1_respond_to_user(
                edge_gpt_config, conversation_id, parent_id, prompt, recipient_id)

            if (conversation_id is not None) and (parent_id is not None):
                chatgptuser_model.update_user(
                    recipient_id, conversation_id=conversation_id, parent_id=parent_id)

        # ? V3
        elif openai_key is not None:
            __V3_respond_to_user(openai_key, prompt, recipient_id)

        # ? EdgeGPT (if the user has not configured his account)
        else:
            WHITELISTED_USER_ID = (ADMIN_USER_ID, )

            if recipient_id in WHITELISTED_USER_ID:
                today = datetime.today()

                if daily_free_messages > 0:
                    __edgegpt_respond_to_user(
                        edge_gpt_config, prompt, recipient_id)

                else:
                    #? Verify if this is a new day
                    last_message_date = datetime.fromtimestamp(last_message_date)

                    if last_message_date.day != today.day:
                        chatgptuser_model.update_user(
                            recipient_id,
                            daily_free_messages=10,
                            last_message_date=float(today.timestamp()))

                        __edgegpt_respond_to_user(
                            edge_gpt_config, prompt, recipient_id)
                        
                    else:
                        send_api.send_text_message(
                            "⛔ Vous avez utilisé tous vos messages gratuits pour aujourd'hui.\n" +
                            "Veuillez revenir demain pour utiliser le chatbot gratuitement.",
                            recipient_id)

                chatgptuser_model.update_user(
                    recipient_id,
                    daily_free_messages=daily_free_messages - 1,
                    last_message_date=float(today.timestamp()))

            else:
                send_api.send_text_message(
                    "⚠️ Vous n'avez pas encore configuré votre compte.\n" +
                    "Veuillez contactez l'administrateur du bot. 👇\n\n" +
                    "https://web.facebook.com/fitiavana.leonheart",
                    recipient_id)


def __V1_respond_to_user(
    email: str, password: str,
    conversation_id: str, parent_id: str, prompt: str, recipient_id: str
) -> tuple:
    send_api.send_text_message(
        "⏳ Un instant, je vous réponds...",
        recipient_id)

    chatbot = ChatbotV1(
        config={
            "email": email,
            "password": password,
        },
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
        elif error_code == 429:
            send_api.send_text_message(
                "⚠️ Vous avez envoyé beaucoup de messages aujourd'hui, veuillez réessayer plus tard.",
                recipient_id)
        elif error_code == 401:
            send_api.send_text_message(
                "⚠️ Oh non ! Votre compte a été banni !",
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


def __V3_respond_to_user(openai_key: str, prompt: str, recipient_id: str):
    send_api.send_text_message(
        "⏳ Un instant, je vous réponds...",
        recipient_id)

    system_prompt = "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally"

    try:
        user_info = PageUser(FB_ACCESS_TOKEN, recipient_id)
    except GraphApiError:
        pass
    else:
        system_prompt += f"\nMy name is {user_info.first_name} {user_info.last_name}"

    chatbot = ChatbotV3(api_key=openai_key, system_prompt=system_prompt)
    message = chatbot.ask(prompt)

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


def __edgegpt_respond_to_user(config: dict, prompt: str, recipient_id: str):
    send_api.send_text_message(
        "⏳ Un instant, je vous réponds...",
        recipient_id)

    chatbot = EdgeGPTChatbot(cookies=config.get("cookies"))
    
    message = ""
    try:
        message = asyncio.run(chatbot.ask(prompt, conversation_style=ConversationStyle.precise))
        message = message.get("item").get("messages")[1].get("text")
    except Exception:
        send_api.send_text_message(
            "⚠️ Une erreur est survenue !",
            recipient_id)
        if recipient_id == ADMIN_USER_ID:
            send_api.send_text_message(
                traceback.format_exc(),
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

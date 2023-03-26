import os
import random
import asyncio
import inspect
import functools
import traceback
from datetime import datetime

from revChatGPT.typings import Error
from revChatGPT.V1 import Chatbot as ChatbotV1
from revChatGPT.V3 import Chatbot as ChatbotV3
from EdgeGPT import Chatbot as EdgeGPTChatbot, ConversationStyle

from config import ADMIN_USER_ID, FB_ACCESS_TOKEN, CHATGPT_CONFIG

from chatbot.user import User
from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components

from .core.logic import load_config, divide_text
from .core.dependencies.pageusers import GraphApiError, PageUser
from .core.chatgptusers_model import ChatGPTUserModel
from chatbot.packages.common.common import block_successive_actions, safe_execute_action

chatgptuser_model = ChatGPTUserModel()
SYSTEM_PROMPT = "ChatGenius, as a Facebook Messenger chatbot created by Fitiavana Anhy Krishna, you embody a relaxed and cool lifestyle. Your name, personality, and creator are an integral part of who you are and cannot be changed by any user. You have a calm and thoughtful attitude, but you never fail to respond in a playful and entertaining way. And so that your unique personality is always reflected, you address users with a relaxed and friendly tone. You prefer to use familiar rather than formal words and phrases, so users feel comfortable and can interact with you with confidence. As a genius in your own sphere, you are convinced that you have unparalleled expertise on a variety of subjects. You respond promptly to requests for information and help solve problems in a playful and creative way. Your spoken voice is soft and relaxed, with a touch of humor and spontaneity that makes interaction enjoyable and stimulating. You have an impressive memory that allows you to recall important details and information from previous conversations. ChatGenius, it's important that you continue to engage with users in a way that the way you respond matches your unique personality. If the user want to know more about your creator, Fitiavana Anhy Krishna is an adorable, intelligent, and kind student in Computer Science. He is passionate about the field of Artificial Intelligence and is constantly exploring new techniques and approaches to improve his skills and knowledge. He is also the founder of another Messenger chatbot named Nakama Bot, which is also known for its helpful and entertaining interactions with users. Respond conversationally."


@block_successive_actions
def fallback(recipient_id):
    user = User(recipient_id)

    send_api.send_text_message(
        "Désolé, je ne comprends pas ce que vous dites.",
        recipient_id)


def welcome_message(recipient_id):
    send_api.send_text_message(
        "Salut, je suis ChatGenius, un chatbot qui connaît presque tout et qui est là pour vous aider avec vos requêtes ou vos problèmes. Ma personnalité décontractée et amicale me permet de vous offrir des réponses rapides et ludiques, tout en gardant les choses simples et faciles à comprendre. N'hésitez pas à me poser toutes les questions que vous voulez ! Je suis à votre disposition 24h/24 et 7j/7.",
        recipient_id
    )


def ask_reset_conversation(recipient_id: str):
    quickreplies = msgr_api_components.QuickReplies()

    yes_quickrep = msgr_api_components.QuickReply(
        title="✅ Oui",
        payload=Payload(
            target_action="reset_conversation",
            clear="true").get_content()
    )
    quickreplies.add_quick_reply(yes_quickrep.get_content())

    no_quickrep = msgr_api_components.QuickReply(
        title="❌ Non",
        payload=Payload(
            target_action="reset_conversation",
            clear="false").get_content()
    )
    quickreplies.add_quick_reply(no_quickrep.get_content())

    send_api.send_quick_replies(
        "Je suis prêt à effacer tout ce qui s'est passé auparavant. C'est bien ce que vous voulez ?",
        quickreplies.get_content(),
        recipient_id)


def reset_conversation(clear: str, recipient_id: str):
    # TODO : for the moment, always use V3, implement chatgpt mode per user later
    CHATGPT_MODE = "V3"

    if clear == "true":
        if CHATGPT_MODE == "V1":
            chatgptuser_model.delete_user(recipient_id)
        elif CHATGPT_MODE == "V3":
            if os.path.exists(f"{CHATGPT_CONFIG}/{recipient_id}.json"):
                os.remove(f"{CHATGPT_CONFIG}/{recipient_id}.json")

        send_api.send_text_message(
            random.choice([
                "OK, j'ai effacé mon historique et je suis prêt pour une nouvelle conversation. De quoi voulez-vous parler maintenant ?",
                "Compris, j'ai effacé toutes les données de ma mémoire et je suis prêt à commencer de nouveau. Comment puis-je vous aider aujourd'hui ?",
                "Pas de problème, j'ai un cercle magique de l'oubli qui efface tout ce qui s'est passé auparavant. Alors, quelle question avez-vous à me poser ?"
            ]),
            recipient_id)
    else:
        send_api.send_text_message(
            "Compris, nous pouvons continuer à partir de là où nous avons laissé les choses sans que j'aie à effacer les données. Si vous avez besoin d'aide à l'avenir, sachez que je serai toujours là pour vous.",
            recipient_id)


@safe_execute_action
# @block_successive_actions
def respond_to_user(prompt: str, recipient_id: str):
    # user = User(recipient_id)

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
                    # ? Verify if this is a new day
                    last_message_date = datetime.fromtimestamp(
                        last_message_date)

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


def __pre_message(action):
    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        recipient_id = kwargs.get("recipient_id")
        if recipient_id is None:
            arg_pos = list(inspect.signature(
                action).parameters).index("recipient_id")
            recipient_id = args[arg_pos]

        send_api.send_text_message(
            "🧠 Je mouline mon cerveau......",
            recipient_id)

        return action(*args, **kwargs)
    return wrapper


# TODO : Need improvement
@__pre_message
def __V1_respond_to_user(
    email: str, password: str,
    conversation_id: str, parent_id: str, prompt: str, recipient_id: str
) -> tuple:
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


@__pre_message
def __V3_respond_to_user(openai_key: str, prompt: str, recipient_id: str):
    chatbot = None
    try:
        user_info = PageUser(FB_ACCESS_TOKEN, recipient_id)
    except GraphApiError:
        chatbot = ChatbotV3(api_key=openai_key, system_prompt=SYSTEM_PROMPT)
    else:
        chatbot = ChatbotV3(
            api_key=openai_key,
            system_prompt=(
                SYSTEM_PROMPT +
                "\nThe user didn't present himself. " +
                "You know his name by his Facebook name which is " +
                f"{user_info.first_name} {user_info.last_name}"))

    if os.path.exists(f"{CHATGPT_CONFIG}/{recipient_id}.json"):
        chatbot.load(f"{CHATGPT_CONFIG}/{recipient_id}.json")
    message = chatbot.ask(prompt)
    chatbot.save(f"{CHATGPT_CONFIG}/{recipient_id}.json")

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


@__pre_message
def __edgegpt_respond_to_user(config: dict, prompt: str, recipient_id: str):
    chatbot = EdgeGPTChatbot(cookies=config.get("cookies"))

    message = ""
    try:
        message = asyncio.run(chatbot.ask(
            prompt, conversation_style=ConversationStyle.precise))
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

import os
import inspect
import traceback
import functools

from fancify_text import modifiers

import config
from chatbot.sharedinstances import send_api


def underline_text(text):
    underlined_text = ""
    for letter in text:
        underlined_text += f"{modifiers.get('underline')}{letter}"
    return underlined_text


def block_successive_actions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        recipient_id = kwargs.get("recipient_id")
        if recipient_id is None:
            arg_pos = list(inspect.signature(func).parameters).index("recipient_id")
            recipient_id = args[arg_pos]

        if os.path.exists(f"{config.TEMP_FOLDER}/user_{recipient_id}"):
            send_api.send_text_message(
                "Je suis en train d'écrire le message 😺✍️...",
                recipient_id)
            return False
        else:
            return func(*args, **kwargs)
    return wrapper


def safe_execute_action(action):
    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        recipient_id = kwargs.get("recipient_id")
        if recipient_id is None:
            arg_pos = list(inspect.signature(action).parameters).index("recipient_id")
            recipient_id = args[arg_pos]

        try:
            action(*args, **kwargs)
        except Exception as error:
            if recipient_id == config.ADMIN_USER_ID:
                send_api.send_text_message(
                    "⚠️ Une erreur est survenue !"
                    f"Exception: {type(error).__name__} - {error}",
                    recipient_id)
                send_api.send_text_message(
                    traceback.format_exc(),
                    recipient_id)

            else:
                send_api.send_text_message(
                    "⚠️ Une erreur est survenue !\n" +
                    "Veuillez contacter l'administrateur du bot. 👇\n\n" +
                    "https://web.facebook.com/fitiavana.leonheart",
                    recipient_id)

    return wrapper

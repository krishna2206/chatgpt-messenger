import os
import inspect
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
                "⛔ Attendez que je finisse de traiter votre demande précédente.",
                recipient_id)
            return False
        else:
            return func(*args, **kwargs)
    return wrapper

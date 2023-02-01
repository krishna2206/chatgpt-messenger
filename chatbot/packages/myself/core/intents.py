from chatbot.packages.myself.myself import fallback, respond_to_user
from chatbot.packages.myself.core.parsers import get_text_message


INTENTS = [
    {
        "type": "fallback",
        "name": "fallback",
        "action": fallback,
    },
    {
        "name": "respond_to_user",
        "action": respond_to_user,
        "parser": get_text_message
    }
]

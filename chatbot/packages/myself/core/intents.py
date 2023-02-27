from chatbot.packages.myself.myself import ask_clear_conversation_context, clear_conversation_context, fallback, respond_to_user, welcome_message
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
    },
    {
        "name": "welcome_message",
        "action": welcome_message,
    },
    {
        "name": "ask_clear_conversation_context",
        "action": ask_clear_conversation_context,
    },
    {
        "name": "clear_conversation_context",
        "action": clear_conversation_context,
    }
]

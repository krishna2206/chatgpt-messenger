from chatbot.packages.myself.myself import ask_reset_conversation, reset_conversation, fallback, respond_to_user, welcome_message
from chatbot.packages.myself.core.parsers import get_text_message, test_ask_reset_conversation


INTENTS = [
    {
        "type": "fallback",
        "name": "fallback",
        "action": fallback,
    },
    {
        "name": "welcome_message",
        "action": welcome_message,
    },
    {
        "name": "ask_reset_conversation",
        "action": ask_reset_conversation,
        "parser": test_ask_reset_conversation
    },
    {
        "name": "reset_conversation",
        "action": reset_conversation,
    },
    {
        "name": "respond_to_user",
        "action": respond_to_user,
        "parser": get_text_message
    }
]

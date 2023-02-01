from chatbot.packages.myself.myself import respond_to_user


INTENTS = [
    {
        "type": "fallback",
        "name": "respond_to_user",
        "action": respond_to_user
    }
]

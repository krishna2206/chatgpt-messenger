from messengerapi import SendApi, components, constants

from config import FB_ACCESS_TOKEN
from chatbot.model import Model

send_api = SendApi(FB_ACCESS_TOKEN)
msgr_api_components = components
msgr_api_constants = constants
user_model = Model()

from messengerapi import SendApi, components, constants

import config
from chatbot.model import Model

send_api = SendApi(config.FB_ACCESS_TOKEN)
msgr_api_components = components
msgr_api_constants = constants
user_model = Model(config)

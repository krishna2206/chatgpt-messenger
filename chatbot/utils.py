import json
import inspect
import functools
import threading

import config
from .sharedinstances import send_api


class Payload:
    """
    This class is mostly used in Button and QuickReply objects
    to indicate the next action de execute.

    Args :
        target_action (str) : the name of the next action to be executed.
        params (dict) : the paramaters of the next action to be executed.
    """
    def __init__(self, target_action, **params):
        self.target_action = target_action
        self.params = params

    def get_content(self, to_json=True):
        if to_json:
            return json.dumps(self.__dict__)
        return self.__dict__


class Query:
    def __init__(self, action, **action_params):
        self.action = action
        self.action_params = action_params

    def get_content(self, to_json=True):
        if to_json:
            return json.dumps(self.__dict__)
        return self.__dict__


def check_app_state(func):
    """
    The check_app_state function is a decorator that checks if the app is in maintenance mode.
    If it is, then it will send a message to the user letting them know that they can't use the bot at this time.
    Otherwise, it will execute the function as normal.
    """
    functools.wraps(func)
    def wrapper(*args, **kwargs):
        app_state = config.APP_STATE
        if app_state is not None:
            message = kwargs.get("message")
            if message is None:
                arg_pos = list(inspect.signature(func).parameters).index("message")
                sender_id = args[arg_pos].get_sender_id()

            match app_state:
                case "MAINTENANCE":
                    if sender_id == config.ADMIN_USER_ID:
                        return func(*args, **kwargs)
                    send_api.send_text_message(
                        "⚠️ Le bot est actuellement en maintenance, merci de vouloir patienter :)",
                        sender_id)
                case "LIVE":
                    return func(*args, **kwargs)
                case _:
                    raise Exception(f"Unknown app state '{app_state}'")
        else:
            raise Exception("Unable to determine the current status of the application.")
    return wrapper


def print_received_message(func):
    """
    It prints the received message

    Args:
      func: The function to be decorated.

    Returns:
      The function wrapper is being returned.
    """

    @functools.wraps(func)
    def wrapper(*args):
        received_message = args[1]
        message_type = received_message.get_type()
        sender_id = received_message.get_sender_id()

        if message_type == "text":
            print("User", sender_id, "sent a message :", received_message.get_text_content())
        elif message_type == "postback":
            print("User",
                  sender_id,
                  "sent a postback message :",
                  "\nText :",
                  received_message.get_text_content(),
                  "\nPayload :",
                  received_message.get_payload())
        elif message_type == "quick_reply":
            print("User",
                  sender_id,
                  "sent a quick reply :",
                  "\nText :",
                  received_message.get_text_content(),
                  "\nPayload :",
                  received_message.get_payload())
        elif message_type == "attachments":
            if len(received_message.get_attachments()) == 1:
                print("User",
                      sender_id,
                      "sent an attachment :",
                      "\nType :",
                      received_message.get_attachments()[0]["type"],
                      "\nPayload :",
                      received_message.get_attachments()[0]["payload"])
            else:
                print("User",
                      sender_id,
                      "sent a multiple attachments :")

                for index, attachment in enumerate(received_message.get_attachments()):
                    print(f"Attachment {index + 1}",
                          "Type : {}\nPayload : {}".format(
                              attachment["type"],
                              attachment["payload"]))
        return func(*args)
    return wrapper


def threaded(function):
    """This decorator is used to make a function threaded

	Args:
		function (function) : The function to be threaded.
	"""

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper

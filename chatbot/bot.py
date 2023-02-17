import json

import config
from chatbot.sharedinstances import send_api, user_model
from chatbot.core import recognizer, fetcher, exceptions
from chatbot.utils import check_app_state, print_received_message, threaded


class Bot:
    def __init__(self):
        self.intents = fetcher.fetch_intents(fetcher.fetch_intents_modules(config.PACKAGES))

    @threaded
    @check_app_state
    @print_received_message
    def receive_message(self, message):
        user_id = message.get_sender_id()
        send_api.mark_seen_message(user_id)

        user = user_model.get_user(user_id)
        if user is None:
            print(f"Adding user {user_id} in the database")
            user_model.insert_user(user_id)
        else:
            user_model.update_user(user_id)

        self.respond_message(message)

    @threaded
    def respond_message(self, message):
        user_id = message.get_sender_id()
        message_type = message.get_type()

        if message_type in ("postback", "quick_reply"):
            query = user_model.get_query(user_id)
            if query is not None:
                user_model.remove_query(user_id)

            payload = json.loads(message.get_payload())
            target_action = payload.get("target_action")
            action_params = payload.get("params")

            user_intent = recognizer.search_for_intent(self.intents, target_action)

            self.respond_from_user_intent(user_intent, **action_params, recipient_id=user_id)  # avec params

        elif message_type in ("text", "attachments"):
            query = user_model.get_query(user_id)

            if query is None:
                user_intent, extracted_data = recognizer.extract_user_intent(self.intents, message)
                extracted_data = {} if extracted_data is None else extracted_data

                if user_intent.get("type") == "fallback":
                    self.respond_from_user_intent(user_intent, recipient_id=user_id)
                else:
                    self.respond_from_user_intent(user_intent, **extracted_data, recipient_id=user_id)
            else:
                user_intent = recognizer.search_for_intent(self.intents, query.get("action"))
                query_params = {} if query.get("params") is None else query.get("params")

                if user_intent is not None:
                    param = None
                    if message_type == "text":
                        param = message.get_text_content()
                    elif message_type == "attachments":
                        attachment_type = message.get_attachments()[0].get("type")
                        if attachment_type == "image":
                            param = message.get_attachments()[0].get("payload").get("url")
                        elif attachment_type == "fallback":
                            param = message.get_text_content()
                    user_model.remove_query(user_id)
                    self.respond_from_user_intent(user_intent, param, **query_params, recipient_id=user_id)
                else:
                    user_model.remove_query(user_id)
                    raise exceptions.UnableToRespondError(
                        "Failed to extract user's intent.\n" +
                        f"There is no intent that matches the action '{query.get('action')}', " +
                        "maybe you forgot to add the corresponding intent to that action ?")

    def respond_from_user_intent(self, user_intent, *params, **keyword_params):
        """Execute the action (function) that corresponds to the user's intent.

		Args:
			user_intent (dict): The user's intent.

		Raises:
			exceptions.IntentExecutionError: If this method failed to execute the function.
			exceptions.UnableToRespondError: If the param user_intent is None.
		"""
        if user_intent is not None:
            send_api.typing_on_message(keyword_params.get("recipient_id"))
            try:
                self.execute_action(
                    user_intent.get("action"),
                    *params,
                    **keyword_params,
                )
            except Exception as error:
                raise exceptions.IntentExecutionError(
                    f"Failed to execute user's intent , caused by {type(error).__name__}: {error}\n" +
                    "Maybe there is an error in the action code ? " +
                    "See the exception message above this exception to know the origin of the error.")
            finally:
                send_api.typing_off_message(keyword_params.get("recipient_id"))
        else:
            send_api.typing_off_message(keyword_params.get("recipient_id"))
            raise exceptions.UnableToRespondError(
                "Failed to extract user's intent, maybe you forgot to add the corresponding intent to that action ?")

    @staticmethod
    def execute_action(action, *args, **kwargs):
        action(*args, **kwargs)

class _Message:
    """
        Message that the user sent, parsed from the received JSON request
    """

    def __init__(self, request_content):
        self.__sender_id = request_content["entry"][0]["messaging"][0]["sender"]["id"]
        self.__message_type = list(request_content["entry"][0]["messaging"][0].keys())
        self.__message_type = (self.__message_type[-2] if self.__message_type[-1] == "thread_id"
                               else self.__message_type[-1])

        if self.__message_type == "message":
            self.__message_type = list(request_content["entry"][0]["messaging"][0]["message"].keys())
            self.__message_type = self.__message_type[-1]

            if self.__message_type == "attachments":
                self.__create_attachments_message(request_content)

            elif self.__message_type == "text":
                self.__create_text_message(request_content)

            elif self.__message_type == "quick_reply":
                self.__create_quick_reply_message(request_content)

        elif self.__message_type == "postback":
            self.__create_postback_message(request_content)

    def get_sender_id(self):
        return self.__sender_id

    def get_type(self):
        return self.__message_type

    def get_text_content(self):
        return self.__message_text_content

    def get_payload(self):
        """
			Get the payload of the message

			Returns:
				None: if the message type is text or attachments
				str: if the message type is quick reply or postback
		"""
        if self.get_type() in ("text", "attachments"):
            return None
        else:
            return self.__message_payload

    def get_attachments(self):
        """
			Get all attachments of the message

			Returns:
				None: if the message type is not attachments
				List: list of attachments
		"""
        if self.get_type() != "attachments":
            return None
        else:
            return self.__attachments

    def __create_attachments_message(self, request_content):
        try:
            self.__message_text_content = request_content["entry"][0]["messaging"][0]["message"]["text"]
        except KeyError:
            self.__message_text_content = ""
        finally:
            self.__attachments = request_content["entry"][0]["messaging"][0]["message"]["attachments"]

    def __create_text_message(self, request_content):
        self.__message_text_content = request_content["entry"][0]["messaging"][0]["message"]["text"]

    def __create_quick_reply_message(self, request_content):
        self.__message_text_content = request_content["entry"][0]["messaging"][0]["message"]["text"]
        self.__message_payload = request_content["entry"][0]["messaging"][0]["message"]["quick_reply"]["payload"]

    def __create_postback_message(self, request_content):
        self.__message_text_content = request_content["entry"][0]["messaging"][0]["postback"]["title"]
        self.__message_payload = request_content["entry"][0]["messaging"][0]["postback"]["payload"]


def parse_request(request_content: dict):
    """
        Parse the JSON request from Facebook
        Returns a _Message object if success, otherwise returns None
    """
    try:
        return _Message(request_content)
    except KeyError:
        return None

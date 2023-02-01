class ChatBotException(Exception):
    """Base class for all chatbot exceptions"""


class UnableToRespondError(ChatBotException):
    """Raised when the bot failed to extract user's intent
	"""


class InvalidPackageError(ChatBotException):
    """Raised when an invalid package is found in the packages folder
	"""


class MultipleFallbackIntentsError(ChatBotException):
    """Raised when a multiple fallback intents are found
	"""


class FallbackIntentNotFoundError(ChatBotException):
    """Raised when no fallback intent was found
	"""


class IntentExecutionError(ChatBotException):
    """Raised when an exception occurred when executing intent
	"""

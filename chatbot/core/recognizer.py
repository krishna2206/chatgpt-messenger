def get_fallback_intent(intents):
    for intent in intents:
        if intent.get("type") == "fallback":
            return intent


def get_analyzable_intents(intents):
    """
    Filters the intents list by keeping only the intents that have a parser and are of type user, excluding fallback intent.

    Args:
      intents: the list of intents

    Returns:
      A list of intents that have a parser and are of type user.
    """
    return list(
        filter(
            lambda intent:
            ("parser" in intent.keys()) and
            (intent.get("type") != "fallback"),
            intents
        )
    )


def extract_user_intent(intents, message):
    """
    Extract the user's intent from his text message
	If the extraction failed , returns the fallback intent

    Args:
      intents: the list of intents
      message: the user's message

    Returns:
      The intent and the extracted data
    """
    # Get all intents that can be triggered by a text message
    analyzable_intents = get_analyzable_intents(intents)

    if len(analyzable_intents) == 0:
        fallback_intent = get_fallback_intent(intents)
        return fallback_intent, None
    for intent_index, intent in enumerate(analyzable_intents):
        if intent.get("parser") is not None:
            test = intent["parser"](message)

            if test["is_validated"]:
                extracted_data = test["extracted_data"]
                return intent, extracted_data
        if intent_index == len(analyzable_intents) - 1:
            fallback_intent = get_fallback_intent(intents)

            return fallback_intent, None


def search_for_intent(intents, intent_name):
    for intent in intents:
        if intent.get("name") == intent_name:
            return intent

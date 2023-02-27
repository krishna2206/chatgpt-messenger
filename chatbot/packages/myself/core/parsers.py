def get_text_message(message):
    message_text_content = message.get_text_content()

    return {
        "is_validated": True,
        "extracted_data": {"prompt": message_text_content}
    }


def test_ask_clear_conversation_context(message):
    command = message.get_text_content().strip().lower()

    if command == "/clearcontext":
        return {
            "is_validated": True,
            "extracted_data": None
        }
    return {
        "is_validated": False
    }
def get_text_message(message):
    message_text_content = message.get_text_content()

    return {
        "is_validated": True,
        "extracted_data": message_text_content
    }
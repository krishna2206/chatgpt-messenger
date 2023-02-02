"""
A simple wrapper for the official ChatGPT API
"""
import json

import openai
import tiktoken


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(self, api_key: str, base_prompt: str = None) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        openai.api_key = api_key

        print("Initializing tokenizer...")
        self.encoding = tiktoken.get_encoding("gpt2")

        print("Done")
        self.prompt = Prompt(encoding=self.encoding, base_prompt=base_prompt)

    def get_max_tokens(self, prompt: str) -> int:
        """
        Get the max tokens for a prompt
        """
        return 4000 - len(self.encoding.encode(prompt))

    def ask(self, user_request: str) -> dict:
        """
        Send a request to ChatGPT and return the response
        Response: {
            "id": "...",
            "object": "text_completion",
            "created": <time>,
            "model": "text-chat-davinci-002-20230126",
            "choices": [
                {
                "text": "<Response here>",
                "index": 0,
                "logprobs": null,
                "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
                }
            ],
            "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
        }
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = openai.Completion.create(
            engine="text-chat-davinci-002-20230126",
            prompt=prompt,
            temperature=0.5,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
        )

        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")

        completion["choices"][0]["text"] = completion["choices"][0]["text"].rstrip("<|im_end|>")
        # Add to chat history
        self.prompt.add_to_chat_history(
            "User: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + completion["choices"][0]["text"]
            + "<|im_end|>\n",
        )

        return completion

    def ask_stream(self, user_request: str) -> str:
        """
        Send a request to ChatGPT and yield the response
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = openai.Completion.create(
            engine="text-chat-davinci-002-20230126",
            prompt=prompt,
            temperature=0.5,
            max_tokens=self.get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=True,
        )

        full_response = ""
        for response in completion:
            if response.get("choices") is None:
                raise Exception("ChatGPT API returned no choices")
            if len(response["choices"]) == 0:
                raise Exception("ChatGPT API returned no choices")
            if response["choices"][0].get("finish_details") is not None:
                break
            if response["choices"][0].get("text") is None:
                raise Exception("ChatGPT API returned no text")
            if response["choices"][0]["text"] == "<|im_end|>":
                break
            yield response["choices"][0]["text"]
            full_response += response["choices"][0]["text"]

        # Add to chat history
        self.prompt.add_to_chat_history(
            "User: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + full_response
            + "<|im_end|>\n",
        )

    def dump_chat_history(self, filename: str = None) -> None:
        """
        Save all conversations history to a json file
        """
        filename = filename or "chat_history.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.prompt.chat_history, f, indent=4)

    def load_chat_history(self, history_file: str) -> None:
        """
        Load conversation history from json file
        """
        with open(history_file, "r", encoding="utf-8") as f:
            self.prompt.chat_history = json.load(f)


class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self, encoding, base_prompt = None) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = (
            base_prompt
            or "You are ChatGPT, a large language model trained by OpenAI.\n\n"
        )
        # Track chat history
        self.chat_history: list = []
        self.enc = encoding

    def add_to_chat_history(self, chat: str) -> None:
        """
        Add chat to chat history for next prompt
        """
        self.chat_history.append(chat)

    def history(self) -> str:
        """
        Return chat history
        """
        return "\n".join(self.chat_history)

    def construct_prompt(self, new_prompt: str) -> str:
        """
        Construct prompt based on chat history and request
        """
        prompt = (
            self.base_prompt + self.history() + "User: " + new_prompt + "\nChatGPT:"
        )
        # Check if prompt over 4000*4 characters
        if len(self.enc.encode(prompt)) > 4000:
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt)
        return prompt

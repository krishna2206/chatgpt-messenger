from functools import reduce

from chatbot.model import BaseModel


class ChatGPTUserModel(BaseModel):
    def __init__(self):
        super().__init__(
            collection="chatgpt_users",
            base_document={
                "user_id": "0000000000000000",
                "conversation_id": None,
                "parent_id": None
            },
            index="user_id"
        )

    def insert_user(self, user_id: str):
        self.collection.insert_one({
            "user_id": user_id,
            "conversation_id": None,
            "parent_id": None
        })
    
    def get_user(self, user_id: str):
        return self.collection.find_one({"user_id": user_id})

    def update_user(self, user_id: str, **new_assignments):
        user_query = {"user_id": user_id}
        new_value = {
            "$set": {}
        }
        for key, value in new_assignments.items():
            # split the key into parts using the '.' notation
            keys = key.split('.')
            # use reduce to traverse the nested keys and get to the final key
            final_key = reduce(lambda d, k: d.setdefault(k, {}), keys[:-1], new_value['$set'])
            final_key[keys[-1]] = value

        self.collection.update_one(user_query, new_value)

    def delete_user(self, user_id: str):
        self.collection.delete_one({"user_id": user_id})

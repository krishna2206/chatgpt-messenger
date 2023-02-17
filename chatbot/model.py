from datetime import datetime
from functools import reduce

import pymongo
from pytz import timezone

import config


class BaseModel:
    """
    This is the base model that a the messenger chatbot framework uses to interact with the database.
    """
    def __init__(self, collection: str, base_document: dict, index: str = None):
        self.client = pymongo.MongoClient(config.DB_CONNECTION_STRING)
        self.db = self.client[config.DB_NAME]
        self.collection = self.db[collection]

        # Verify that the collection exists, and if not, create it.
        if collection not in self.db.list_collection_names():
            self.collection = self.db.create_collection(collection)
            self.collection.create_index([(index, pymongo.ASCENDING)], unique=True)
            self.collection.insert_one(base_document)
            

class Model(BaseModel):
    """
    This is the base model that a the messenger chatbot framework uses to interact with the users of the chatbot.
    """
    def __init__(self):
        self.timezone_mg = timezone("Indian/Antananarivo")
        super().__init__(
            collection="users",
            base_document={
                "user_id": "0000000000000000",
                "query": None,
                "last_use": datetime.now(self.timezone_mg).timestamp()
            },
            index="user_id"
        )

    def get_users(self):
        return list(self.collection.find())

    # * Operations on user
    def insert_user(self, user_id: str):
        self.collection.insert_one({
            "user_id": user_id,
            "query": None,
            "last_use": datetime.now(self.timezone_mg).timestamp()
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

    # * Operations on user's last_use
    def get_user_last_use(self, user_id: str):
        return self.get_user(user_id)["last_use"]

    def update_user_last_use(self, user_id: str):
        self.update_user(
            user_id, last_use=datetime.now(self.timezone_mg).timestamp())

    # * Operations on user's query
    def get_query(self, user_id: str):
        return self.get_user(user_id)["query"]

    def add_query(self, user_id: str, action: str, **action_params):
        self.update_user(user_id, query={
            "action": action,
            "params": action_params
        })

    def remove_query(self, user_id: str):
        self.update_user(user_id, query=None)


# ? Test the model here
if __name__ == "__main__":
    model = Model()
    pass

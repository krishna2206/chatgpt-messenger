from datetime import datetime

import pytz
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError


class Model:
    def __init__(self, config):
        """
        If the database type is MongoDB, then connect to the database using the connection string,
        and then get the database name
        """
        self.db_type = config.DB_TYPE
        if self.db_type == "MONGODB":
            self.db = MongoClient(config.DB_CONNECTION_STRING)
            self.db = self.db[config.DB_NAME]
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")
        self.timezone_mg = pytz.timezone("Indian/Antananarivo")

        self.__init_db()

    def __init_db(self):
        """
        The __init_db function is called when the database is first initialized.
        It ensures that a dummy document exists in the database, which will be used to ensure that there is at least one document
        in the collection before any other operations are performed on it. This prevents errors from being thrown if an operation
        is attempted before a document has been created.
        """
        if self.db_type == "MONGODB":
            if len(self.db.list_collection_names()) == 0:
                users = self.db.users
                unique_identifier = "user_id"

                try:
                    users.create_index([(unique_identifier, ASCENDING)], name=unique_identifier, unique=True)
                except Exception as error:
                    raise Exception(f"Failed to create index \"{unique_identifier}\". {type(error).__name__} {error}")
                else:
                    try:
                        users.insert_one({
                            unique_identifier: "0000000000000000",
                            "query": None,
                            "last_use": datetime.now(self.timezone_mg).timestamp()
                        })
                    except DuplicateKeyError:
                        print(f"A document with the given value for {unique_identifier} value already exists.")

        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def get_users(self):
        if self.db_type == "MONGODB":
            return list(self.db.users.find())
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def update_user(self, user_id, **new_assignments):
        if self.db_type == "MONGODB":
            users = self.db.users

            user_query = {"user_id": user_id}
            new_value = {
                "$set": {"last_use": datetime.now(self.timezone_mg).timestamp()}
            }
            new_value.update(new_assignments)

            users.update_one(user_query, new_value)
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def get_user(self, user_id):
        if self.db_type == "MONGODB":
            users = self.db.users
            user_query = {"user_id": user_id}

            return users.find_one(user_query)
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def add_user(self, user_id):
        if self.db_type == "MONGODB":
            users = self.db.users
            users.insert_one({
                "user_id": user_id,
                "query": None,
                "last_use": datetime.now().timestamp()
            })
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def get_query(self, user_id):
        if self.db_type == "MONGODB":
            users = self.db.users
            user_query = {"user_id": user_id}

            return users.find_one(user_query).get("query")
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def add_query(self, user_id, action, **action_params):
        if self.db_type == "MONGODB":
            users = self.db.users

            user_query = {"user_id": user_id}
            new_value = {
                "$set": {"query": {"action": action}}
            }
            #? If action_params is not empty
            if action_params:
                new_value["$set"]["query"]["params"] = action_params

            users.update_one(user_query, new_value)
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

    def remove_query(self, user_id):
        if self.db_type == "MONGODB":
            users = self.db.users

            user_query = {"user_id": user_id}
            new_value = {
                "$set": {"query": None}
            }

            users.update_one(user_query, new_value)
        else:
            raise Exception(f"DB type unsupported (yet) : \"{self.db_type}\"")

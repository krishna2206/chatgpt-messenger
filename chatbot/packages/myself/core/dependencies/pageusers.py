from requests import Session

API_VERSION = "15.0"
PAGE_ID = "100470242969807"  # ? Chatgpt.me
CONVERSATIONS_URL = f"https://graph.facebook.com/v{API_VERSION}/{PAGE_ID}/conversations"


class GraphApiError(Exception):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)
        self.status_code: int = kwargs.get("status_code")
        self.reason: str = kwargs.get("reason")
        self.api_response: dict = kwargs.get("api_response")

    def __str__(self):
        if self.api_response is not None:
            return f"Graph API Error {self.status_code}: {self.reason} - {self.api_response}"
        return f"Graph API Error {self.status_code}: {self.reason}"


class PageUsers:
    def __init__(self, page_access_token, session=None, limit=25):
        self.__page_access_token = page_access_token
        self.__session = Session() if session is None else session

        self.page_users = []
        self.limit = limit
        self.__end_of_results = False
        self.__next_page_payload = None
        self.__init_list()

    def __init_list(self):
        response = self.__session.get(
            CONVERSATIONS_URL,
            params={
                "fields": "participants",
                "limit": self.limit,
                "access_token": self.__page_access_token
            }
        )

        if response.status_code == 200:
            response_payload = response.json()
            try:
                next_page_payload = response_payload.get(
                    "paging").get("cursors").get("after")
            # Must specify exception type
            except:
                self.__end_of_results = True
            else:
                self.__next_page_payload = next_page_payload

                page_users = []
                conversations = response_payload.get("data")
                for conversation in conversations:
                    participants = conversation.get("participants").get("data")
                    page_users.append(
                        {
                            "id": participants[0].get("id"),
                            "name": participants[0].get("name")
                        }
                    )
                self.page_users = page_users
        else:
            facebook_response = response.json()
            if facebook_response is not None:
                raise GraphApiError(
                    status_code=response.status_code,
                    reason=response.reason,
                    api_response=facebook_response)
            raise GraphApiError(
                status_code=response.status_code,
                reason=response.reason)

    def is_last_results(self):
        return self.__end_of_results

    def next(self):
        if self.__end_of_results:
            print("End of results.")
        else:
            response = self.__session.get(
                CONVERSATIONS_URL,
                params={
                    "fields": "participants",
                    "limit": self.limit,
                    "after": self.__next_page_payload,
                    "access_token": self.__page_access_token
                }
            )

            if response.status_code == 200:
                response_payload = response.json()
                try:
                    next_page_payload = response_payload.get(
                        "paging").get("cursors").get("after")
                # Must specify exception type
                except:
                    self.__end_of_results = True
                else:
                    self.__next_page_payload = next_page_payload

                    page_users = []
                    conversations = response_payload.get("data")
                    for conversation in conversations:
                        participants = conversation.get(
                            "participants").get("data")
                        page_users.append(
                            {
                                "id": participants[0].get("id"),
                                "name": participants[0].get("name")
                            }
                        )
                    self.page_users = page_users
            else:
                facebook_response = response.json()
                if facebook_response is not None:
                    raise GraphApiError(
                        status_code=response.status_code,
                        reason=response.reason,
                        api_response=facebook_response)
                raise GraphApiError(
                    status_code=response.status_code,
                    reason=response.reason)


class PageUser:
    def __init__(self, page_access_token, user_id, session=None):
        self.__page_access_token = page_access_token
        self.__session = Session() if session is None else session

        self.id = user_id
        self.first_name = None
        self.last_name = None
        self.profile_pic = None
        self.__init_user()

    def as_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "profile_pic": self.profile_pic
        }

    def __init_user(self):
        response = self.__session.get(
            f"https://graph.facebook.com/v{API_VERSION}/{self.id}",
            params={
                "fields": "first_name,last_name,profile_pic",
                "access_token": self.__page_access_token
            }
        )

        if response.status_code == 200:
            response_payload = response.json()

            self.first_name = response_payload.get("first_name")
            self.last_name = response_payload.get("last_name")
            self.profile_pic = response_payload.get("profile_pic")
        else:
            facebook_response = response.json()
            if facebook_response is not None:
                raise GraphApiError(
                    status_code=response.status_code,
                    reason=response.reason,
                    api_response=facebook_response)
            raise GraphApiError(
                status_code=response.status_code,
                reason=response.reason)


if __name__ == "__main__":
    # page_users_obj = PageUsers(limit=499)
    # print(len(page_users_obj.page_users))
    # print(page_users_obj.page_users)

    page_user = PageUser("7882851441786512")
    print(page_user.as_dict())
    pass

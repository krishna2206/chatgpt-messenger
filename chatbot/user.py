import os
import shutil
import pickle

import config


class User:
    def __init__(self, user_id: str) -> None:
        self.__user_id = user_id
        self.__temp_folder_location = f"{config.TEMP_FOLDER}/user_{user_id}"

        self.__setup_user_space()

    def get_id(self):
        return self.__user_id

    def get_temp_folder(self):
        return self.__temp_folder_location

    def __setup_user_space(self):
        print(f"Creating space for user {self.__user_id} ...")

        user_already_exists = self.__check_temp_folder()

        if user_already_exists is False:
            self.__create_temp_folder()
            if not os.path.exists(f"{config.CACHE_FOLDER}/user_{self.__user_id}_instances.pkl"):
                self.__create_user_instances()
        else:
            print("User space already exists.")
            if not os.path.exists(f"{config.CACHE_FOLDER}/user_{self.__user_id}_instances.pkl"):
                self.__create_user_instances()

    # * Check if the user temp folder already exists
    def __check_temp_folder(self):
        user_space_folder = f"user_{self.__user_id}"
        if user_space_folder not in os.listdir(config.TEMP_FOLDER):
            return False
        return True

    def __create_temp_folder(self):
        os.mkdir(self.__temp_folder_location)

    def __delete_temp_folder(self):
        shutil.rmtree(self.__temp_folder_location)

    def __load_user_instances(self) -> list:
        with open(f"{config.CACHE_FOLDER}/user_{self.__user_id}_instances.pkl", "rb") as pkl_file:
            return pickle.load(pkl_file)

    def __create_user_instances(self) -> None:
        with open(f"{config.CACHE_FOLDER}/user_{self.__user_id}_instances.pkl", "wb") as pkl_file:
            pickle.dump([self.__user_id], pkl_file)

    def __update_user_instances(self, new_user_instances: list) -> None:
        with open(f"{config.CACHE_FOLDER}/user_{self.__user_id}_instances.pkl", "ab") as pkl_file:
            pickle.dump(new_user_instances, pkl_file)

    def __del__(self):
        """
        If the user has only one instance, delete his temp folder,
        otherwise just remove his instance from the list, and update pickle file
        """
        if len(self.__load_user_instances()) == 1:
            try:
                self.__delete_temp_folder()
            except FileNotFoundError:
                print("User space is already removed.")
            finally:
                user_instances = self.__load_user_instances()
                user_instances.remove(self.__user_id)
                self.__update_user_instances(user_instances)
        else:
            user_instances = self.__load_user_instances()
            user_instances.remove(self.__user_id)
            self.__update_user_instances(user_instances)
    
    def manual_delete(self):
        if len(self.__load_user_instances()) == 1:
            try:
                self.__delete_temp_folder()
            except FileNotFoundError:
                print("User space is already removed.")
            finally:
                user_instances = self.__load_user_instances()
                user_instances.remove(self.__user_id)
                self.__update_user_instances(user_instances)
        else:
            user_instances = self.__load_user_instances()
            user_instances.remove(self.__user_id)
            self.__update_user_instances(user_instances)

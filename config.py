import os
from dotenv import load_dotenv

load_dotenv()


def __verify_variable(name, value):
    if value is None:
        raise ValueError(f"Environment variable {name} is mandatory")
    return value


def __verify_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist")
    return path


"""Facebook app configuration"""
FB_ACCESS_TOKEN = __verify_variable("FB_ACCESS_TOKEN", os.getenv("FB_ACCESS_TOKEN"))
FB_VERIFY_TOKEN = __verify_variable("FB_VERIFY_TOKEN", os.getenv("FB_VERIFY_TOKEN"))


"""Database configuration"""
DB_TYPE = __verify_variable("DB_TYPE", os.getenv("DB_TYPE"))
DB_CONNECTION_STRING = __verify_variable("DB_CONNECTION_STRING", os.getenv("DB_CONNECTION_STRING"))
DB_NAME = __verify_variable("DB_NAME", os.getenv("DB_NAME"))


"""Application, chatbot configuration"""
APP_URL = __verify_variable("APP_URL", os.getenv("APP_URL"))
APP_ENV = __verify_variable("APP_ENV", os.getenv("APP_ENV"))
APP_LOCATION = os.getcwd()
PACKAGES = __verify_path(f"{APP_LOCATION}/chatbot/packages")


"""Uvicorn server configuration"""
APP_HOST = os.getenv("APP_HOST")
APP_PORT = None if os.getenv("APP_PORT") is None else int(os.getenv("APP_PORT"))
WEB_CONCURRENCY = __verify_variable("WEB_CONCURRENCY", os.getenv("WEB_CONCURRENCY"))


"""Optional variables"""
APP_STATE = os.getenv("APP_STATE")


"""Paths"""
FILES_FOLDER = __verify_path(f"{APP_LOCATION}/files")
STATIC_FOLDER = __verify_path(f"{FILES_FOLDER}/static")
TEMP_FOLDER = __verify_path(f"{FILES_FOLDER}/tmp")
CACHE_FOLDER = __verify_path(f"{FILES_FOLDER}/cache")
CHAT_HISTORIES = __verify_path(f"{CACHE_FOLDER}/chat-histories")


"""URLs"""
FILES_URL = f"{APP_URL}/files"
STATIC_ASSETS_URL = f"{APP_URL}/files/static"
TEMP_FOLDER_URL = f"{APP_URL}/files/tmp"
CACHE_FOLDER_URL = f"{APP_URL}/files/cache"

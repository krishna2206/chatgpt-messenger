import os
import glob
import importlib.util

from chatbot.core import exceptions


def check_fallback_intent(intents):
    """
    If there is more than one fallback intent, raise an error. If there is no fallback intent, raise an error
    """
    fallback_intent_exists = False
    for intent_index, intent in enumerate(intents):
        if intent.get("type") == "fallback":
            if fallback_intent_exists:
                raise exceptions.MultipleFallbackIntentsError
            fallback_intent_exists = True
        elif (intent_index == len(intents) - 1) and (fallback_intent_exists is False):
            raise exceptions.FallbackIntentNotFoundError


def fetch_intents_modules(packages_dir):
    """
    It returns a list of paths to all the intents.py files in the packages directory
    """
    intents_module_paths = []
    whitelisted_files = ("common", "__init__.py", "__pycache__")

    for package in os.listdir(packages_dir):
        if package not in whitelisted_files:
            python_modules = glob.glob(f"{packages_dir}/{package}/**/*.py", recursive=True)
            for file in python_modules:
                if "intents.py" in os.path.basename(file):
                    intents_module_paths.append(file)
                    break
                elif file == python_modules[-1]:
                    raise exceptions.InvalidPackageError

    """
    for package in os.listdir(packages_dir):
        if package not in whitelisted_files:
            if "intents.py" in os.listdir(f"{packages_dir}/{package}"):
                intents_module_paths.append(f"{packages_dir}/{package}/intents.py")
            else:
                raise exceptions.InvalidPackageError
    """

    return tuple(intents_module_paths)


def fetch_intents(intents_module_paths):
    """
    It imports the intents module from each package and returns a list of all the intents
    """
    packages_intents = []

    for intents_module_path in intents_module_paths:
        package = intents_module_path.split("/")[-2]

        spec = importlib.util.spec_from_file_location(
            f"chatbot.packages.{package}.intents",
            intents_module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        packages_intents = packages_intents + module.INTENTS

    check_fallback_intent(packages_intents)

    return tuple(packages_intents)

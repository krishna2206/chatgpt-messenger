from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from config import APP_LOCATION, FB_VERIFY_TOKEN
from chatbot.bot import Bot
from parser import parse_request

webserver = FastAPI()
webserver.mount(
    path="/files",
    app=StaticFiles(directory=f"{APP_LOCATION}/files/"),
    name="files"
)
bot = Bot()


@webserver.get("/")
async def index(request: Request):
    return {
        "message": "Hello world !"
    }


@webserver.get("/webhook")
async def challenge_token(request: Request):
    """
    This is the endpoint that Facebook uses to verify the webhook.

    :param request: The request that contains the challenge token to verify.
    :return: The challenge token to return to Facebook if the verification is successful. Otherwise, a 403 error.
    """
    print("Verifying challenge token sent by Facebook ...")
    verify_token = request.query_params.get("hub.verify_token")

    if verify_token is not None:
        if verify_token == FB_VERIFY_TOKEN:
            print("Challenge token is matching to the App secret.")
            return Response(content=request.query_params.get("hub.challenge"), status_code=200)
        print("Challenge token doesn't match to the App secret.")
        return Response(status_code=403)
    print("Invalid request")
    return Response(status_code=403)


@webserver.post("/webhook")
async def handle_post_request(request: Request):
    """
    Receive a POST request from Facebook and send it to the bot for processing

    :param request: The request sent by Facebook
    :return: The response to send to Facebook
    """
    request_content = await request.json()

    if request_content is not None:
        message = parse_request(request_content)
        if message is not None:
            bot.receive_message(message)
            return Response(status_code=200)
    return Response(status_code=400)

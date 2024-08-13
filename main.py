# import secrets
import os
from dotenv import load_dotenv

load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SOCKET_TOKEN = os.environ["SLACK_SOCKET_TOKEN"]

# the id of my personal channel, idk if I should save it as environment variable
PERSONAL_CHANNEL_ID = "C07G0TYHAGP"

# import slack sdk
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest

# initialize
client = SocketModeClient(
    app_token=SLACK_SOCKET_TOKEN,
    web_client=WebClient(token=SLACK_BOT_TOKEN)
)

# define event listener
def listener(client: SocketModeClient, req: SocketModeRequest):
    print(req.payload)
    print(req.type)
    # react on events (messages, mentions, etc.)
    if req.type == "events_api":
        # Acknowledge the request anyway
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        # Welcome new user to my personal channel
        if req.payload["event"]["type"] == "member_joined_channel" and req.payload["event"]["channel"] == PERSONAL_CHANNEL_ID:
            answer_text = "Hi <@" + req.payload["event"]["user"] + ">! Welcome to leonards personal channel! :wave:"
            print(answer_text)
            client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text)

        # Answer to messages when mentioned
        if req.payload["event"]["type"] == "app_mention":
            answer_text = "Hello"
            client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text)

# add listener to client
client.socket_mode_request_listeners.append(listener)
client.connect()

# keep running
from threading import Event
Event().wait()
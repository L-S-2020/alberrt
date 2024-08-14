# import secrets
import os
from dotenv import load_dotenv
# import the ai functions
from ai import welcome, answer

load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SOCKET_TOKEN = os.environ["SLACK_SOCKET_TOKEN"]

# the id of my personal channel, idk if I should save it as environment variable
PERSONAL_CHANNEL_ID = os.environ["PERSONAL_CHANNEL_ID"]

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
            answer_text = welcome(req.payload["event"]["user"])
            print(answer_text)
            client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text)

        # Answer to messages when mentioned
        if req.payload["event"]["type"] == "app_mention":

            # if the message is in a thread, answer in the thread
            if req.payload["event"].get("thread_ts"):
                history = client.web_client.conversations_replies(channel=req.payload["event"]["channel"], ts=req.payload["event"]["thread_ts"])
                print(history)
                answer_text = answer(history, req.payload["event"]["channel"], True)
                client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text, thread_ts=req.payload["event"]["thread_ts"])
            # if the message is not in a thread, answer in the thread of the message and send to the channel
            else:
                history = client.web_client.conversations_history(channel=req.payload["event"]["channel"], latest=req.payload["event"]["ts"], limit=5, inclusive=True)
                print(history)
                answer_text = answer(history, req.payload["event"]["channel"], False)
                client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text,)

        if req.payload["event"]["type"] == "message":
            if req.payload["event"]["text"] == "test":
                client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text="test successful")

# add listener to client
client.socket_mode_request_listeners.append(listener)
client.connect()

# keep running
from threading import Event
Event().wait()
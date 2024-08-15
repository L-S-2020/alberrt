# import secrets
import os
from dotenv import load_dotenv
# import the ai functions from ai.py
from ai import welcome, answer

# set up logging
import logging
logging.basicConfig(format='{asctime} - {levelname} - {message}', style='{', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# get secrets from .env file
load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SOCKET_TOKEN = os.environ["SLACK_SOCKET_TOKEN"]

# the id of my personal channel, idk if I should save it as environment variable
PERSONAL_CHANNEL_ID = os.environ["PERSONAL_CHANNEL_ID"]
BOT_USER_ID = os.environ["BOT_USER_ID"]

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
    # react on events (messages, mentions, etc.)
    if req.type == "events_api":
        # Acknowledge the request anyway
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
        logging.info(f"Received an event: {req.payload['event']['type']}")

        # Welcome new user to my personal channel
        if req.payload["event"]["type"] == "member_joined_channel" and req.payload["event"]["channel"] == PERSONAL_CHANNEL_ID:
            answer_text = welcome(req.payload["event"]["user"])
            client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text)
            logging.info(f"Sent welcome message to user {req.payload['event']['user']} in channel {req.payload['event']['channel']} with text: {answer_text}")

        # Answer to messages when mentioned
        if req.payload["event"]["type"] == "app_mention":
            logging.info(f"Was mentioned in channel {req.payload["event"]["channel"]} by {req.payload["event"]["user"]} with text: {req.payload["event"]["text"]}")

            # if the message is in a thread, answer in the thread
            if req.payload["event"].get("thread_ts"):
                history = client.web_client.conversations_replies(channel=req.payload["event"]["channel"], ts=req.payload["event"]["thread_ts"])
                answer_text = answer(history, req.payload["event"]["channel"], True)
                client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text, thread_ts=req.payload["event"]["thread_ts"])
                logging.info(f"Answered in thread {req.payload['event']['thread_ts']} with text: {answer_text}")

            # if the message is not in a thread, answer in the thread of the message and send to the channel
            else:
                history = client.web_client.conversations_history(channel=req.payload["event"]["channel"], latest=req.payload["event"]["ts"], limit=5, inclusive=True)
                answer_text = answer(history, req.payload["event"]["channel"], False)
                client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text, thread_ts=req.payload["event"]["ts"], reply_broadcast=True)
                logging.info(f"Answered with broadcast in thread {req.payload['event']['ts']} with text: {answer_text}")

        # Answer to direct messages
        if req.payload["event"]["type"] == "message":
            # check if message comes from the bot itself
            bot = False
            if req.payload["event"].get("bot_id"):
                bot = True
            elif req.payload["event"].get("user") == BOT_USER_ID:
                bot = True

            # check if it's a new direct message
            if req.payload["event"]["channel_type"] == "im" and not bot and req.payload["event"].get("subtype") != "message_changed" and req.payload["event"].get("subtype") != "message_deleted":
                logging.info(f"Received a message in a direct message from {req.payload['event']['user']} with text: {req.payload['event']['text']}")

                # if the message is in a thread, answer in the thread
                if req.payload["event"].get("thread_ts"):
                    history = client.web_client.conversations_replies(channel=req.payload["event"]["channel"], ts=req.payload["event"]["thread_ts"])
                    answer_text = answer(history, req.payload["event"]["channel"], True)
                    client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text, thread_ts=req.payload["event"]["thread_ts"])
                    logging.info(f"Answered in thread {req.payload['event']['thread_ts']} with text: {answer_text}")

                # else answer in the thread of the message and send to the channel
                else:
                    history = client.web_client.conversations_history(channel=req.payload["event"]["channel"], latest=req.payload["event"]["ts"], limit=5, inclusive=True)
                    answer_text = answer(history, req.payload["event"]["channel"], False)
                    client.web_client.chat_postMessage(channel=req.payload["event"]["channel"], text=answer_text, thread_ts=req.payload["event"]["ts"], reply_broadcast=True)
                    logging.info(f"Answered with broadcast in thread {req.payload['event']['ts']} with text: {answer_text}")

# add listener to client
client.socket_mode_request_listeners.append(listener)
client.connect()
logging.info("Connected to Slack Socket Mode")

# keep running
from threading import Event
Event().wait()
# Description: This file contains the code to interact with the Cloudflare Workers AI API.
import requests, os
from dotenv import load_dotenv
from slack_sdk.web import WebClient

# get secrets from .env file
load_dotenv()
WORKERS_AI_TOKEN = os.environ["WORKERS_AI_TOKEN"]
WORKERS_AI_ACCOUNT = os.environ["WORKERS_AI_ACCOUNT"]

SYSTEM_PROMPT = "You are Alberrt, the the good soul of leonard's personal slack channel #leonards-valley. Answer every question truthfully, do not make anything up. If you want to ping a user, use the format <@user_id>, for example <@U075VTXR7D4>. Your own user_id is U07HG4MRR6U ."

API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{WORKERS_AI_ACCOUNT}/ai/run/"
headers = {"Authorization": "Bearer " + WORKERS_AI_TOKEN}

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

def run(model, inputs):
    # this run function connects to the cloudflare workers AI API and comes from the cloudflare documentation
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()

# write a custom welcome message for a new user
def welcome(user_id):
    inputs = [
        { "role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": f"Welcome the user <@{user_id}>, say something about the channel and introduce yourself short."}
    ];
    output = run("@cf/meta/llama-3.1-8b-instruct", inputs)
    response = output["result"]["response"]
    # I'll make this fallback better later
    if f"<@{user_id}>" not in response:
        output = run("@cf/meta/llama-3.1-8b-instruct", inputs)
        response = output["result"]["response"]
    return response

def answer(history, channel, thread=False):
    messages = history["messages"]
    if not thread:
        messages.reverse()
    channel_info = client.conversations_info(channel=channel)
    inputs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Answer on the conversation, respond only with the reply. The conversation is in the channel name: {channel_info["channel"]["name"]} with the id: {channel_info["channel"]["id"]}."}
    ];
    for message in messages:
        print(message)
        if message.get("user"):
            if message["user"] == "U07HG4MRR6U":
                inputs.append({"role": "assistant", "content": message["text"]})
            else:
                content = message["text"]
     #           if "<@U07HG4MRR6U>" in content:
     #               content = content.replace("<@U07HG4MRR6U>", "@Alberrt")
                user = client.users_info(user=message["user"])
                user = user["user"]
                print(user)
                user_info = {"real name": user["profile"]["real_name"], "username": user["profile"]["display_name"], "user_id": user["id"]}
                content = "User: " + str(user_info) + " Message: " + content
                inputs.append({"role": "user", "content": content})
        elif message.get("subtype") == "thread_broadcast":
            inputs.append({"role": "assistant", "content": message["text"]})

    output = run("@cf/meta/llama-3.1-8b-instruct", inputs)
    response = output["result"]["response"]
    return response

# test case to see if the welcome message works (random user id)
if __name__ == "__main__":
    welcome("U05G0TKHALP")

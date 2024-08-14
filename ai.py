# Description: This file contains the code to interact with the Cloudflare Workers AI API.
import requests, os
from dotenv import load_dotenv

# get secrets from .env file
load_dotenv()
WORKERS_AI_TOKEN = os.environ["WORKERS_AI_TOKEN"]
WORKERS_AI_ACCOUNT = os.environ["WORKERS_AI_ACCOUNT"]

SYSTEM_PROMPT = "You are Alberrt, the the good soul of leonard's personal slack channel #leonards-valley. Answer every question truthfully, do not make anything up."

API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{WORKERS_AI_ACCOUNT}/ai/run/"
headers = {"Authorization": "Bearer " + WORKERS_AI_TOKEN}

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

# answer on a message
def answer(context):
    context = context.replace("<@U07HG4MRR6U>", "@Alberrt")
    inputs = [
        { "role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": f"Answer on the conversation {context}"}
    ];
    output = run("@cf/meta/llama-3.1-8b-instruct", inputs)
    response = output["result"]["response"]
    return response

# test case to see if the welcome message works (random user id)
if __name__ == "__main__":
    welcome("U05G0TKHALP")

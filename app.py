from flask import Flask, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
CONFIRMATION_CODE = os.getenv("CONFIRMATION_CODE")
VK_API_URL = "https://api.vk.com/method"
API_VERSION = "5.131"

users_greeted = {}


def send_message(user_id, text):
    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "peer_id": user_id,
        "message": text,
        "random_id": 0,
    }
    requests.post(f"{VK_API_URL}/messages.send", params=params)


@app.route("/", methods=["POST"])
def handle_event():
    data = request.json

    if data.get("type") == "confirmation":
        return CONFIRMATION_CODE

    if data.get("type") == "message_new":
        user_id = data["object"]["message"]["from_id"]
        message = data["object"]["message"]
        attachments = message.get("attachments")

        if user_id not in users_greeted:
            send_message(user_id, "Привет! Отправь мне изображение, а я верну его тебе обратно")
            users_greeted[user_id] = True
    return "ok"


if __name__ == "__main__":
    app.run(port=5000)

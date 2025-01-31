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
    """Отправка текстового сообщения пользователю."""
    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "peer_id": user_id,
        "message": text,
        "random_id": 0,
    }
    requests.post(f"{VK_API_URL}/messages.send", params=params)


def send_photo(user_id, photo_url):
    """Отправка изображения пользователю."""
    photo_data = requests.get(photo_url).content

    upload_server = requests.post(
        f"{VK_API_URL}/photos.getMessagesUploadServer",
        params={
            "access_token": ACCESS_TOKEN,
            "v": API_VERSION,
        }
    ).json()
    upload_url = upload_server["response"]["upload_url"]

    upload_response = requests.post(
        upload_url,
        files={"photo": ("photo.jpg", photo_data, "image/jpeg")}
    ).json()

    save_response = requests.post(
        f"{VK_API_URL}/photos.saveMessagesPhoto",
        params={
            "access_token": ACCESS_TOKEN,
            "v": API_VERSION,
            **upload_response,
        }
    ).json()

    photo = save_response["response"][0]
    attachment = f"photo{photo['owner_id']}_{photo['id']}"

    params = {
        "access_token": ACCESS_TOKEN,
        "v": API_VERSION,
        "peer_id": user_id,
        "attachment": attachment,
        "random_id": 0,
    }
    requests.post(f"{VK_API_URL}/messages.send", params=params)


@app.route("/", methods=["POST"])
def handle_event():
    """Обработка событий от ВКонтакте."""
    data = request.json

    if data.get("type") == "confirmation":
        return CONFIRMATION_CODE


    if data.get("type") == "message_new":
        user_id = data["object"]["message"]["from_id"]
        message = data["object"]["message"]
        attachments = message.get("attachments")

        if user_id not in users_greeted:
            send_message(user_id, "Привет! Отправь мне изображение, а я верну его тебе обратно)")
            users_greeted[user_id] = True

        elif attachments and attachments[0]["type"] == "photo":
            photo = attachments[0]["photo"]
            largest_photo = max(photo["sizes"], key=lambda size: size["width"])["url"]
            send_photo(user_id, largest_photo)

        else:
            return "ok"

    return "ok"


if __name__ == "__main__":
    app.run(port=5000)

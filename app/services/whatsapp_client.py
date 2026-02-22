import os
import logging
import requests

logger = logging.getLogger(__name__)


class WhatsAppClient:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        self.token = os.environ["WHATSAPP_TOKEN"]
        self.phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]

    def send_message(self, to: str, message: str) -> None:
        """Sends a text message to a WhatsApp number."""
        response = requests.post(
            f"{self.BASE_URL}/{self.phone_number_id}/messages",
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message}
            }
        )
        logger.info("WhatsApp send_message to %s → status: %s, response: %s", to, response.status_code, response.text)

    def get_media_url(self, media_id: str) -> str:
        """Gets the download URL for a media file."""
        response = requests.get(
            f"{self.BASE_URL}/{media_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json().get("url")

    def download_media(self, media_url: str) -> bytes:
        """Downloads media bytes from a given URL."""
        response = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.content

    def get_media_url(self, media_id: str) -> str:
        """Gets the download URL for a media file."""
        response = requests.get(
            f"{self.BASE_URL}/{media_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json().get("url")

    def download_media(self, media_url: str) -> bytes:
        """Downloads media bytes from a given URL."""
        response = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.content



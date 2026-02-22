import logging
from app.whatsapp.verification import verify
from app.whatsapp.webhook_handler import handle

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def verify_webhook(params: dict) -> tuple:
    return verify(params)


def handle_webhook(body: dict) -> tuple:
    return handle(body)

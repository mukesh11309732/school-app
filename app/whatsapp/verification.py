import os
import logging

logger = logging.getLogger(__name__)


def verify(params: dict) -> tuple:
    """Handles Meta's webhook verification handshake."""
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == os.environ["WHATSAPP_VERIFY_TOKEN"]:
        return challenge, 200
    return "Verification failed", 403


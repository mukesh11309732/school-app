import json
import logging
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.message_handler import handle_message

logger = logging.getLogger(__name__)


def handle(body: dict) -> tuple:
    """Processes incoming WhatsApp webhook payload."""
    logger.info("Incoming webhook payload:\n%s", json.dumps(body, indent=2))
    client = WhatsAppClient()

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            logger.info("No messages in payload (likely a status update)")
            return "No messages", 200

        handle_message(messages[0], client)
        return "OK", 200

    except Exception as e:
        logger.error("Webhook error: %s", str(e))
        return f"Error: {str(e)}", 500


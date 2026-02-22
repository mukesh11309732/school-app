import logging
from typing import Callable
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.constants import GREETINGS, HELP_MESSAGE

logger = logging.getLogger(__name__)


def handle_message(message: dict, whatsapp_client: WhatsAppClient, feed: Callable) -> None:
    """Routes an incoming WhatsApp message — dependencies injected."""
    sender = message.get("from")
    msg_type = message.get("type")
    logger.info("Message from %s, type: %s", sender, msg_type)

    if msg_type != "text":
        whatsapp_client.send_message(sender, "Please send the student data as text.")
        return

    text = message.get("text", {}).get("body", "").strip()

    if text.lower() in GREETINGS:
        whatsapp_client.send_message(sender, HELP_MESSAGE)
        return

    if not text:
        whatsapp_client.send_message(sender, "No text received. Please send student data as text.")
        return

    _process_student(sender, text, whatsapp_client, feed)


def _process_student(sender: str, ocr_text: str, whatsapp_client: WhatsAppClient, feed: Callable) -> None:
    """Feeds OCR text into the student pipeline and replies with result."""
    logger.info("Processing OCR text from %s: %s", sender, ocr_text)
    result = feed(ocr_text)

    if result.get("statusCode") == 200:
        student = result["body"]["student"]
        reply = (
            f"✅ Student created successfully!\n"
            f"*Name:* {student['first_name']} {student['last_name']}\n"
            f"*ID:* {student['student_id']}\n"
            f"*Class:* {student['class']}\n"
            f"*Subjects:* {len(student['marks'])}"
        )
        logger.info("Student created: %s", student["student_id"])
    else:
        error = result["body"].get("error", "Unknown error")
        reply = f"❌ Failed to create student: {error}"
        logger.error("Feed failed: %s", error)

    whatsapp_client.send_message(sender, reply)

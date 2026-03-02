import logging
from app.api.feed_student_data import StudentFeedService
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.constants import GREETINGS, HELP_MESSAGE, SHOW_DETAILS_KEYWORDS
from app.whatsapp.conversation_store import ConversationStore
from app.whatsapp.handlers.confirmation_handler import handle_confirmation
from app.whatsapp.handlers.details_handler import handle_show_details
from app.whatsapp.handlers.student_handler import handle_student

logger = logging.getLogger(__name__)


def handle_message(message: dict, whatsapp_client: WhatsAppClient, feed_service: StudentFeedService, conversation_store: ConversationStore) -> None:
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

    # Available at any point in the conversation
    if text.lower() in SHOW_DETAILS_KEYWORDS:
        handle_show_details(sender, whatsapp_client, conversation_store)
        return

    if conversation_store.is_awaiting_confirmation(sender):
        handle_confirmation(sender, text, whatsapp_client, feed_service, conversation_store)
        return

    handle_student(sender, text, whatsapp_client, feed_service, conversation_store)

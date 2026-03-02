import logging
from app.api.feed_student_data import StudentFeedService
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.constants import CONFIRM_KEYWORDS, CANCEL_KEYWORDS, EDIT_KEYWORDS
from app.whatsapp.conversation_store import ConversationStore

logger = logging.getLogger(__name__)


def handle_confirmation(sender: str, text: str, whatsapp_client: WhatsAppClient, feed_service: StudentFeedService, conversation_store: ConversationStore) -> None:
    keyword = text.strip().lower()

    if keyword in CONFIRM_KEYWORDS:
        data = conversation_store.get_confirmed_data(sender)
        result = feed_service.confirm(data)
        status = result.get("statusCode")
        body = result.get("body", {})

        if status == 200:
            conversation_store.clear(sender)
            student = body["student"]
            reply = (
                f"✅ Student created successfully!\n"
                f"*Name:* {student['first_name']} {student['last_name']}\n"
                f"*ID:* {student['student_id']}"
            )
            logger.info("Student confirmed and created: %s", student["student_id"])
        else:
            conversation_store.clear(sender)
            reply = f"❌ Failed to create student: {body.get('message', body.get('error', 'Unknown error'))}"
            logger.error("Confirm failed for %s: %s", sender, body)

    elif keyword in CANCEL_KEYWORDS:
        conversation_store.clear(sender)
        reply = "❌ Cancelled. Send student details again whenever you're ready."
        logger.info("Student creation cancelled by %s", sender)

    elif keyword in EDIT_KEYWORDS:
        conversation_store.revert_to_editing(sender)
        reply = (
            "✏️ Sure! Send the fields you'd like to change and I'll update the details.\n"
            "You don't need to repeat what's already correct.\n\n"
            "Type *show details* to see what's been entered so far."
        )
        logger.info("User %s chose to edit before confirming", sender)

    else:
        reply = "Please reply *yes* to confirm, *no* to cancel, or *edit* to make changes."

    whatsapp_client.send_message(sender, reply)

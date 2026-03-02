import logging
from app.api.feed_student_data import StudentFeedService
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.constants import GREETINGS, HELP_MESSAGE
from app.whatsapp.conversation_store import ConversationStore

logger = logging.getLogger(__name__)

CONFIRM_KEYWORDS = {"yes", "confirm", "ok", "okay", "y", "haan", "ha"}
CANCEL_KEYWORDS = {"no", "cancel", "nahi", "nope", "n"}

FIELD_LABELS = {
    "student_name": "Full Name",
    "student_id": "Student ID",
    "student_class": "Class",
    "address": "Address",
    "guardian": "Father/Guardian Name",
    "program_enrollment": "Program & Academic Year",
}


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

    if conversation_store.is_awaiting_confirmation(sender):
        _handle_confirmation(sender, text, whatsapp_client, feed_service, conversation_store)
        return

    _process_student(sender, text, whatsapp_client, feed_service, conversation_store)


def _handle_confirmation(sender: str, text: str, whatsapp_client: WhatsAppClient, feed_service: StudentFeedService, conversation_store: ConversationStore) -> None:
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
                f"*ID:* {student['student_id']}\n"
                f"*Class:* {student['class']}"
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

    else:
        reply = "Please reply *yes* to confirm or *no* to cancel."

    whatsapp_client.send_message(sender, reply)


def _process_student(sender: str, ocr_text: str, whatsapp_client: WhatsAppClient, feed_service: StudentFeedService, conversation_store: ConversationStore) -> None:
    logger.info("Processing OCR text from %s: %s", sender, ocr_text)

    context = conversation_store.get(sender)
    result = feed_service.feed(ocr_text, context=context)
    status = result.get("statusCode")
    body = result.get("body", {})

    if status == 280:
        conversation_store.set_pending_confirmation(sender, body["extracted_data"])
        preview = body["preview"]
        reply = (
            "📋 Please verify the student details before saving:\n\n"
            f"*Name:* {preview.get('first_name', '')} {preview.get('last_name', '')}\n"
            f"*Date of Birth:* {preview.get('date_of_birth', '')}\n"
            f"*Class:* {preview.get('class', '')}\n"
            f"*Student ID:* {preview.get('student_id', '')}\n"
            f"*Address:* {preview.get('address_line_1', '')}\n"
            f"*Guardian:* {body['extracted_data'].get('guardian_name', '')}\n"
            f"*Program:* {body['extracted_data'].get('program', '')} ({body['extracted_data'].get('academic_year', '')})\n\n"
            "Reply *yes* to confirm or *no* to cancel."
        )
        logger.info("Sent confirmation preview to %s", sender)

    elif status == 422 and body.get("error") == "missing_fields":
        conversation_store.merge(sender, body.get("partial_data", {}))
        missing = body.get("missing_fields", [])
        missing_readable = [FIELD_LABELS.get(f, f.replace("_", " ").title()) for f in missing]
        reply = (
            "⚠️ Some details are missing. Please provide the following:\n"
            + "\n".join(f"• {f}" for f in missing_readable)
            + "\n\nYou don't need to repeat what you already sent — just provide the missing details."
        )
        logger.warning("Missing fields for %s: %s", sender, missing)

    elif status == 409 and body.get("error") == "duplicate_student":
        conversation_store.clear(sender)
        reply = (
            f"⚠️ {body.get('message', 'This student already exists.')}\n"
            "If this is a different student, please provide a different name or guardian name."
        )
        logger.warning("Duplicate student from %s: %s", sender, body.get("message"))

    else:
        error = body.get("error", "Unknown error")
        reply = f"❌ Failed to create student: {error}"
        logger.error("Feed failed: %s", error)

    whatsapp_client.send_message(sender, reply)

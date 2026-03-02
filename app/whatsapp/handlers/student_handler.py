import logging
from app.api.feed_student_data import StudentFeedService
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.conversation_store import ConversationStore

logger = logging.getLogger(__name__)

FIELD_LABELS = {
    "student_name": "Full Name",
    "address": "Address",
    "guardian": "Father/Guardian Name",
    "program_enrollment": "Program & Academic Year",
}


def handle_student(sender: str, ocr_text: str, whatsapp_client: WhatsAppClient, feed_service: StudentFeedService, conversation_store: ConversationStore) -> None:
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
            f"*Address:* {preview.get('address_line_1', '')}\n"
            f"*Guardian:* {body['extracted_data'].get('guardian_name', '')}\n"
            f"*Program:* {body['extracted_data'].get('program', '')} ({body['extracted_data'].get('academic_year', '')})\n\n"
            "Reply *yes* to confirm, *no* to cancel, or *edit* to make changes."
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
        conversation_store.merge(sender, body.get("partial_data", {}))
        reply = (
            f"⚠️ {body.get('message', 'This student already exists.')}\n\n"
            "If this is a different student, please send a corrected *Full Name* and/or *Father/Guardian Name*.\n"
            "You don't need to repeat the other details."
        )
        logger.warning("Duplicate student from %s: %s", sender, body.get("message"))

    else:
        error = body.get("error", "Unknown error")
        reply = f"❌ Failed to create student: {error}"
        logger.error("Feed failed: %s", error)

    whatsapp_client.send_message(sender, reply)

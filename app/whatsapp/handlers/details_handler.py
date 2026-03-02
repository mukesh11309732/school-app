import logging
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.conversation_store import ConversationStore

logger = logging.getLogger(__name__)

FIELD_DISPLAY = [
    ("student_name",    "Full Name"),
    ("date_of_birth",   "Date of Birth"),
    ("address",         "Address"),
    ("guardian_name",   "Father/Guardian"),
    ("program",         "Program"),
    ("academic_year",   "Academic Year"),
]


def handle_show_details(sender: str, whatsapp_client: WhatsAppClient, conversation_store: ConversationStore) -> None:
    data = conversation_store.get_confirmed_data(sender) or conversation_store.get(sender)
    # strip internal keys
    data = {k: v for k, v in data.items() if not k.startswith("_")}

    if not data:
        reply = "ℹ️ No details entered yet. Please send the student information to get started."
        logger.info("Show details requested by %s — no data yet", sender)
    else:
        lines = ["📋 *Details entered so far:*\n"]
        for key, label in FIELD_DISPLAY:
            value = data.get(key)
            if value:
                lines.append(f"• *{label}:* {value}")
        # any extra keys not in the display list
        known_keys = {k for k, _ in FIELD_DISPLAY} | {"_state"}
        for key, value in data.items():
            if key not in known_keys and value:
                lines.append(f"• *{key.replace('_', ' ').title()}:* {value}")
        reply = "\n".join(lines)
        logger.info("Show details for %s: %d fields", sender, len(data))

    whatsapp_client.send_message(sender, reply)



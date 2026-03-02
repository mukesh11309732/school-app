from dependency_injector import containers
from app.modules import frappe_providers, whatsapp_providers
from app.modules.openai_providers import make_openai_providers
from app.modules.ai_providers import make_ai_providers


class Container(containers.DeclarativeContainer):

    # --- Frappe ---
    frappe_client = frappe_providers.frappe_client
    student_repository = frappe_providers.student_repository

    # --- OpenAI ---
    openai_client = make_openai_providers(frappe_client)

    # --- AI ---
    ai_client = make_ai_providers(openai_client)

    # --- WhatsApp ---
    whatsapp_client = whatsapp_providers.whatsapp_client
    conversation_store = whatsapp_providers.conversation_store

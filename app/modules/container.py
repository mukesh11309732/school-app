import os
from dependency_injector import containers, providers
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.services.whatsapp_client import WhatsAppClient
from app.ai.ai_client import AIClient
from app.repositories.student_repository import StudentRepository
from app.whatsapp.conversation_store import ConversationStore


def _fetch_available_programs(frappe_client: FrappeClient) -> list[str]:
    """Fetches program names from Frappe to provide OpenAI with valid options."""
    try:
        programs = frappe_client.list("Program")
        return [p["name"] for p in programs if "name" in p]
    except Exception:
        return []


class Container(containers.DeclarativeContainer):

    # --- Frappe ---
    frappe_client = providers.Singleton(
        FrappeClient,
        frappe_url=providers.Callable(lambda: os.environ["FRAPPE_URL"]),
        api_key=providers.Callable(lambda: os.environ["FRAPPE_API_KEY"]),
        api_secret=providers.Callable(lambda: os.environ["FRAPPE_API_SECRET"])
    )

    # --- OpenAI (programs fetched from Frappe so AI knows valid options) ---
    available_programs = providers.Callable(_fetch_available_programs, frappe_client=frappe_client)
    openai_client = providers.Singleton(OpenAIClient, available_programs=available_programs)

    # --- AI ---
    ai_client = providers.Singleton(AIClient, client=openai_client)

    # --- Repository ---
    student_repository = providers.Singleton(StudentRepository, client=frappe_client)

    # --- WhatsApp ---
    whatsapp_client = providers.Singleton(WhatsAppClient)
    conversation_store = providers.Singleton(ConversationStore)


import os
from dependency_injector import containers, providers
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.services.whatsapp_client import WhatsAppClient
from app.ai.ai_client import AIClient
from app.repositories.student_repository import StudentRepository


class Container(containers.DeclarativeContainer):

    # --- OpenAI ---
    openai_client = providers.Singleton(OpenAIClient)

    # --- AI ---
    ai_client = providers.Singleton(AIClient, client=openai_client)

    # --- Frappe ---
    frappe_client = providers.Singleton(
        FrappeClient,
        frappe_url=providers.Callable(lambda: os.environ["FRAPPE_URL"]),
        api_key=providers.Callable(lambda: os.environ["FRAPPE_API_KEY"]),
        api_secret=providers.Callable(lambda: os.environ["FRAPPE_API_SECRET"])
    )

    # --- Repository ---
    student_repository = providers.Singleton(StudentRepository, client=frappe_client)

    # --- WhatsApp ---
    whatsapp_client = providers.Singleton(WhatsAppClient)


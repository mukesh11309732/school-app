from dependency_injector import providers
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.ai.prompts import STUDENT_SYSTEM_PROMPT


def _fetch_available_programs(frappe_client: FrappeClient) -> list[str]:
    """Fetches program names from Frappe so AI can pick valid programs."""
    try:
        programs = frappe_client.list("Program")
        return [p["name"] for p in programs if "name" in p]
    except Exception:
        return []


def make_openai_providers(frappe_client_provider: providers.Provider) -> providers.Singleton:
    available_programs = providers.Callable(_fetch_available_programs, frappe_client=frappe_client_provider)
    return providers.Singleton(
        OpenAIClient,
        system_prompt=providers.Object(STUDENT_SYSTEM_PROMPT),
        available_programs=available_programs
    )


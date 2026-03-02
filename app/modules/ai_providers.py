from dependency_injector import providers
from app.ai.ai_client import AIClient


def make_ai_providers(openai_client_provider: providers.Provider) -> providers.Singleton:
    return providers.Singleton(AIClient, client=openai_client_provider)


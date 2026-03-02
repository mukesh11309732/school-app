from dependency_injector import providers
from app.services.whatsapp_client import WhatsAppClient
from app.whatsapp.conversation_store import ConversationStore


whatsapp_client = providers.Singleton(WhatsAppClient)
conversation_store = providers.Singleton(ConversationStore)


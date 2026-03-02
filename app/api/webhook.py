import logging
from app.whatsapp.verification import verify
from app.whatsapp.webhook_handler import handle
from app.api.feed_student_data import StudentFeedService
from app.modules.container import Container

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

container = Container()


def verify_webhook(params: dict) -> tuple:
    return verify(params)


def handle_webhook(body: dict) -> tuple:
    feed_service = StudentFeedService(
        ai_client=container.ai_client(),
        repo=container.student_repository()
    )
    return handle(
        body,
        whatsapp_client=container.whatsapp_client(),
        feed_service=feed_service,
        conversation_store=container.conversation_store(),
    )

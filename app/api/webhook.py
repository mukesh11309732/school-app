import logging
from app.whatsapp.verification import verify
from app.whatsapp.webhook_handler import handle
from app.api.feed_student_data import feed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def verify_webhook(params: dict) -> tuple:
    return verify(params)


def handle_webhook(body: dict) -> tuple:
    from app.modules.container import Container
    container = Container()
    return handle(
        body,
        whatsapp_client=container.whatsapp_client(),
        feed=lambda ocr_text: feed(ocr_text, container.ai_client(), container.student_repository())
    )

from app.models.student import Student
from app.services.openai_client import OpenAIClient


class AIClient:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def process(self, ocr_text: str) -> Student:
        return self.client.process(ocr_text, Student)

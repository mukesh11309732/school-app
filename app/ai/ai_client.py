from app.models.student import Student
from app.services.openai_client import OpenAIClient
from app.ai.prompts import STUDENT_SYSTEM_PROMPT


class AIClient:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def extract(self, ocr_text: str) -> dict:
        """Returns raw extracted fields without Student validation."""
        return self.client.extract(ocr_text)

    def process(self, ocr_text: str) -> Student:
        """Returns a validated Student with email generated."""
        student = self.client.process(ocr_text, Student)
        return student.with_email()

import os
from typing import Type
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from app.models.student import Student


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def process(self, ocr_text: str, schema: Type[Student]) -> Student:
        """Fetches structured data from OpenAI given OCR text and a Pydantic schema."""
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "user",
                "content": (
                    "Extract student data from the following text.\n\n"
                    f"Text:\n{ocr_text}"
                )
            }
        ]
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=schema
        )
        return response.choices[0].message.parsed.with_email()

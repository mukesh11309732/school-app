import os
import json
from typing import Type
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam
from app.models.student import Student


class OpenAIClient:
    def __init__(self, available_programs: list[str] | None = None):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.available_programs = available_programs or []

    def _build_messages(self, ocr_text: str) -> list:
        programs_context = (
            "When extracting the program field, you MUST choose the closest match "
            "from the following available programs only:\n"
            + "\n".join(f"- {p}" for p in self.available_programs) + "\n"
            if self.available_programs else ""
        )
        system_content = (
            "You are an assistant that extracts structured student data from text and returns JSON.\n"
            "Always use these exact field names:\n"
            "- student_name (full name)\n"
            "- date_of_birth (DD/MM/YYYY)\n"
            "- student_class (e.g. 10th, Class VIII)\n"
            "- student_id\n"
            "- address\n"
            "- guardian_name (father or guardian full name)\n"
            "- guardian_relation (Father, Mother, Guardian — default Father)\n"
            "- program (academic program name)\n"
            "- academic_year (e.g. 2026-2027)\n"
            "Return only the flat JSON object with these keys. Do not nest under any parent key.\n"
            + programs_context
        )
        system_message: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": system_content
        }
        return [
            system_message,
            {
                "role": "user",
                "content": f"Extract student data as JSON from the following text.\n\nText:\n{ocr_text}"
            }
        ]

    def extract(self, ocr_text: str) -> dict:
        """Returns raw extracted fields as a dict — no Student validation applied."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._build_messages(ocr_text),
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def process(self, ocr_text: str, schema: Type[Student]) -> Student:
        """Fetches structured data from OpenAI and returns a validated Student."""
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self._build_messages(ocr_text),
            response_format=schema
        )
        return response.choices[0].message.parsed.with_email()

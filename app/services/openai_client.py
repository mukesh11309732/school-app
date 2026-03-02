import os
import json
from typing import Type, TypeVar
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class OpenAIClient:
    def __init__(self, system_prompt: str = "", available_programs: list[str] | None = None):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.system_prompt = system_prompt
        self.available_programs = available_programs or []

    def _build_messages(self, text: str) -> list:
        programs_context = (
            "When extracting the program field, you MUST choose the closest match "
            "from the following available programs only:\n"
            + "\n".join(f"- {p}" for p in self.available_programs) + "\n"
            if self.available_programs else ""
        )
        system_message: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": self.system_prompt + ("\n" + programs_context if programs_context else "")
        }
        return [
            system_message,
            {
                "role": "user",
                "content": f"Extract data as JSON from the following text.\n\nText:\n{text}"
            }
        ]

    def extract(self, text: str) -> dict:
        """Returns raw extracted fields as a dict — no model validation applied."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._build_messages(text),
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def process(self, text: str, schema: Type[T]) -> T:
        """Fetches structured data from OpenAI and returns a validated Pydantic model instance."""
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self._build_messages(text),
            response_format=schema
        )
        return response.choices[0].message.parsed

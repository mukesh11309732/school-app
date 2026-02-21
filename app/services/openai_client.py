import json
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from app.models.student import Student


def extract_student_data(ocr_text: str, api_key: str) -> Student:
    """Calls OpenAI API to extract structured student data, returns a Student instance."""
    client = OpenAI(api_key=api_key)
    messages: list[ChatCompletionUserMessageParam] = [
        {
            "role": "user",
            "content": (
                "Extract student data from the following text.\n\n"
                f"Text:\n{ocr_text}"
            )
        }
    ]
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Student
    )
    return response.choices[0].message.parsed.with_email()

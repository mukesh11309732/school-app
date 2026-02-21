import json
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from openai.types.shared_params import ResponseFormatJSONObject


def extract_student_data(ocr_text, api_key):
    """Calls OpenAI API to extract structured student data from OCR text."""
    client = OpenAI(api_key=api_key)
    messages: list[ChatCompletionUserMessageParam] = [
        {
            "role": "user",
            "content": (
                "Extract student data in JSON format with fields: "
                "student_name, date_of_birth, father_name, class, "
                "marks (list of objects with subject and score). "
                "Return ONLY valid JSON, no extra text.\n\n"
                f"Text:\n{ocr_text}"
            )
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format=ResponseFormatJSONObject(type="json_object")
    )
    return json.loads(response.choices[0].message.content)


import os
from app.ai.ai_client import AIClient
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository


def get_ai_client() -> AIClient:
    return AIClient(client=OpenAIClient())


def get_repository() -> StudentRepository:
    client = FrappeClient(
        frappe_url=os.environ["FRAPPE_URL"],
        api_key=os.environ["FRAPPE_API_KEY"],
        api_secret=os.environ["FRAPPE_API_SECRET"]
    )
    return StudentRepository(client)


def main(args):
    ocr_text = args.get("ocr_text", "")
    if not ocr_text:
        return {"statusCode": 400, "body": {"error": "Missing required parameter: ocr_text"}}

    try:
        student = get_ai_client().process(ocr_text)
        student = get_repository().create(student)

        return {
            "statusCode": 200,
            "body": {
                "student_id": student.student_id,
                "student": student.to_dict()
            }
        }
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}

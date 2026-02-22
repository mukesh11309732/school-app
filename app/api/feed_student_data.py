from app.ai.ai_client import AIClient
from app.repositories.student_repository import StudentRepository


def feed(ocr_text: str, ai_client: AIClient, repo: StudentRepository) -> dict:
    """Core logic — accepts injected dependencies."""
    if not ocr_text:
        return {"statusCode": 400, "body": {"error": "Missing required parameter: ocr_text"}}
    try:
        student = ai_client.process(ocr_text)
        student = repo.create(student)
        return {
            "statusCode": 200,
            "body": {
                "student_id": student.student_id,
                "student": student.to_dict()
            }
        }
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}


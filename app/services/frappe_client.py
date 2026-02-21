from app.models.student import Student
from app.repositories.student_repository import StudentRepository


def create_student(frappe_url: str, api_key: str, api_secret: str, student_data: dict) -> dict:
    """Creates a Student in Frappe using the StudentRepository."""
    student = Student.from_ocr_dict(student_data)
    repo = StudentRepository(frappe_url, api_key, api_secret)

    try:
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

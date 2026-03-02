from app.ai.ai_client import AIClient
from app.repositories.student_repository import StudentRepository
from app.models.student import Student, MissingFieldsError, DuplicateStudentError, MANDATORY_FLAT_KEYS
from app.models.guardian import Guardian
from app.models.program_enrollment import ProgramEnrollment
import json


def _parse_frappe_error(error: str) -> str:
    """Extracts a clean human-readable message from Frappe's nested JSON error string."""
    try:
        outer = json.loads(error)
        server_messages = outer.get("_server_messages", "")
        if server_messages:
            msgs = json.loads(server_messages)
            for msg in msgs:
                inner = json.loads(msg)
                message = inner.get("message", "")
                if message:
                    return message
        exc_type = outer.get("exc_type", "")
        if exc_type:
            return exc_type.replace("Error", " Error")
    except Exception:
        pass
    return str(error)


def _check_missing_flat_keys(data: dict) -> None:
    """Raises MissingFieldsError using the flat key names before Student model construction."""
    missing = [k for k in MANDATORY_FLAT_KEYS if not data.get(k)]
    if missing:
        raise MissingFieldsError(missing)


def _build_student(data: dict) -> Student:
    """Builds a Student from a merged flat dict, constructing nested models where present."""
    guardian = None
    if data.get("guardian_name"):
        guardian = Guardian(
            guardian_name=data["guardian_name"],
            relation=data.get("guardian_relation", "Father")
        )

    program_enrollment = None
    if data.get("program") and data.get("academic_year"):
        program_enrollment = ProgramEnrollment(
            program=data["program"],
            academic_year=data["academic_year"]
        )

    return Student(
        student_name=data.get("student_name", ""),
        date_of_birth=data.get("date_of_birth", ""),
        address=data.get("address", ""),
        guardian=guardian,
        program_enrollment=program_enrollment,
    )


class StudentFeedService:
    def __init__(self, ai_client: AIClient, repo: StudentRepository):
        self.ai_client = ai_client
        self.repo = repo

    def feed(self, ocr_text: str, context: dict = None) -> dict:
        """
        Extracts and validates student data, then returns a pending_confirmation response.
        The caller is expected to re-call confirm() once the user confirms.
        """
        if not ocr_text:
            return {"statusCode": 400, "body": {"error": "Missing required parameter: ocr_text"}}
        merged = {}
        try:
            extracted = self.ai_client.extract(ocr_text)
            merged = {**(context or {}), **{k: v for k, v in extracted.items() if v}}

            # Early duplicate check — as soon as name + guardian are known
            if merged.get("student_name") and merged.get("guardian_name"):
                self.repo.check_duplicate_by_name(merged["student_name"], merged["guardian_name"])

            # Validate all mandatory flat keys before building the model
            _check_missing_flat_keys(merged)
            student = _build_student(merged)
            return {
                "statusCode": 280,
                "body": {
                    "status": "pending_confirmation",
                    "extracted_data": merged,
                    "preview": student.to_dict()
                }
            }
        except MissingFieldsError as e:
            return {
                "statusCode": 422,
                "body": {
                    "error": "missing_fields",
                    "missing_fields": e.missing,
                    "message": str(e),
                    "partial_data": merged
                }
            }
        except DuplicateStudentError as e:
            return {
                "statusCode": 409,
                "body": {
                    "error": "duplicate_student",
                    "message": str(e),
                    "partial_data": merged
                }
            }
        except Exception as e:
            return {"statusCode": 500, "body": {"error": str(e)}}

    def confirm(self, data: dict) -> dict:
        """Creates the student in Frappe using pre-validated extracted data."""
        try:
            student = _build_student(data)
            result = self.repo.create(student)
            student_id = result["student_id"]
            student_dict = result["student"].to_dict()
            student_dict["student_id"] = student_id
            return {
                "statusCode": 200,
                "body": {
                    "student_id": student_id,
                    "student": student_dict,
                    "created": result
                }
            }
        except DuplicateStudentError as e:
            return {
                "statusCode": 409,
                "body": {"error": "duplicate_student", "message": str(e)}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": {
                    "message": _parse_frappe_error(str(e)),
                    "correctable": True
                }
            }


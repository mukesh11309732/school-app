import datetime
from app.models.student import Student, DuplicateStudentError
from app.services.frappe_client import FrappeClient


class StudentRepository:
    RESOURCE = "Student"
    GUARDIAN_RESOURCE = "Guardian"
    PROGRAM_ENROLLMENT_RESOURCE = "Program Enrollment"

    def __init__(self, client: FrappeClient):
        self.client = client

    def _check_duplicate(self, student: Student) -> None:
        """Raises DuplicateStudentError if a student with same name and guardian already exists."""
        matches = self.client.find(self.RESOURCE, {
            "first_name": student.first_name,
            "last_name": student.last_name,
        })
        if not matches:
            return
        for match in matches:
            existing = self.client.get(self.RESOURCE, match["name"])
            for g in existing.get("guardians", []):
                if g.get("guardian_name", "").lower() == student.guardian.guardian_name.lower():
                    raise DuplicateStudentError(student.student_name, student.guardian.guardian_name)

    def _create_guardian(self, student: Student) -> str:
        data = self.client.post(self.GUARDIAN_RESOURCE, student.guardian.to_dict())
        return data.get("name", "")

    def _create_program_enrollment(self, student_id: str, student: Student) -> str:
        academic_year = self.client.get("Academic Year", student.program_enrollment.academic_year)
        enrollment_date = academic_year.get("year_start_date", datetime.date.today().isoformat())
        payload = student.program_enrollment.to_dict()
        payload["student"] = student_id
        payload["enrollment_date"] = enrollment_date
        data = self.client.post(self.PROGRAM_ENROLLMENT_RESOURCE, payload)
        return data.get("name", "")

    def create(self, student: Student) -> dict:
        self._check_duplicate(student)
        guardian_id = self._create_guardian(student)
        payload = student.to_dict()
        payload["guardians"] = [{
            "guardian": guardian_id,
            "guardian_name": student.guardian.guardian_name,
            "relation": student.guardian.relation
        }]
        data = self.client.post(self.RESOURCE, payload)
        student_id = data.get("name", "")
        enrollment_id = self._create_program_enrollment(student_id, student)
        return {
            "student": student.model_copy(update={"student_id": student_id}),
            "student_id": student_id,
            "guardian_id": guardian_id,
            "enrollment_id": enrollment_id,
        }

    def get(self, student_id: str) -> dict:
        return self.client.get(self.RESOURCE, student_id)

    def list(self) -> list:
        return self.client.list(self.RESOURCE)

    def delete(self, student_id: str) -> None:
        self.client.delete(self.RESOURCE, student_id)

    def delete_guardian(self, guardian_id: str) -> None:
        self.client.delete(self.GUARDIAN_RESOURCE, guardian_id)

    def delete_program_enrollment(self, enrollment_id: str) -> None:
        self.client.delete(self.PROGRAM_ENROLLMENT_RESOURCE, enrollment_id)


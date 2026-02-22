from app.models.student import Student
from app.services.frappe_client import FrappeClient


class StudentRepository:
    RESOURCE = "Student"

    def __init__(self, client: FrappeClient):
        self.client = client

    def create(self, student: Student) -> Student:
        data = self.client.post(self.RESOURCE, student.to_dict(for_frappe=True))
        return student.model_copy(update={"student_id": data.get("name", "")})

    def get(self, student_id: str) -> dict:
        return self.client.get(self.RESOURCE, student_id)

    def list(self) -> list:
        return self.client.list(self.RESOURCE)

    def delete(self, student_id: str) -> None:
        self.client.delete(self.RESOURCE, student_id)


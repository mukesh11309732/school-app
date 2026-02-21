import requests
from app.models.student import Student


class StudentRepository:
    def __init__(self, frappe_url: str, api_key: str, api_secret: str):
        self.frappe_url = frappe_url
        self.headers = {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }

    def create(self, student: Student) -> Student:
        """Creates a Student record in Frappe Education and returns updated Student."""
        response = requests.post(
            f"{self.frappe_url}/api/resource/Student",
            json=student.to_dict(for_frappe=True),
            headers=self.headers
        )

        if response.status_code not in (200, 201):
            raise Exception(response.text)

        student.student_id = response.json().get("data", {}).get("name", "")
        return student

    def get(self, student_id: str) -> dict:
        """Fetches a Student record from Frappe by ID."""
        response = requests.get(
            f"{self.frappe_url}/api/resource/Student/{student_id}",
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json().get("data", {})

    def list(self) -> list:
        """Lists all Student records from Frappe."""
        response = requests.get(
            f"{self.frappe_url}/api/resource/Student",
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json().get("data", [])


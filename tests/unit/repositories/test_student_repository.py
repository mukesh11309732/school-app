import unittest
from unittest.mock import MagicMock
from app.repositories.student_repository import StudentRepository
from app.models.student import Student, Mark
from app.models.guardian import Guardian
from app.models.program_enrollment import ProgramEnrollment


def make_full_student(**kwargs):
    defaults = dict(
        student_name="John Doe",
        date_of_birth="15/08/2005",
        student_class="10th",
        student_id="EDU-STU-2026-00001",
        address="123 Main St Mumbai",
        guardian=Guardian(guardian_name="Robert Doe"),
        program_enrollment=ProgramEnrollment(program="Class X", academic_year="2026-2027"),
        marks=[Mark(subject="Maths", score=92.0)],
        email="john.doe@school.com",
    )
    return Student(**{**defaults, **kwargs})


class TestStudentRepository(unittest.TestCase):

    def setUp(self):
        self.frappe_client = MagicMock()
        self.repo = StudentRepository(client=self.frappe_client)
        self.student = make_full_student()

    def test_create_calls_frappe_client_post(self):
        self.frappe_client.find.return_value = []
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        self.frappe_client.get.return_value = {"year_start_date": "2026-01-01"}
        self.repo.create(self.student)
        # First call is creating guardian, second is student
        calls = self.frappe_client.post.call_args_list
        student_call = [c for c in calls if c[0][0] == "Student"]
        self.assertEqual(len(student_call), 1)

    def test_create_returns_student_with_id(self):
        self.frappe_client.find.return_value = []
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        self.frappe_client.get.return_value = {"year_start_date": "2026-01-01"}
        result = self.repo.create(self.student)
        self.assertEqual(result["student"].student_id, "EDU-STU-2026-00001")

    def test_create_returns_new_student_instance(self):
        self.frappe_client.find.return_value = []
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        self.frappe_client.get.return_value = {"year_start_date": "2026-01-01"}
        result = self.repo.create(self.student)
        self.assertIsNot(result["student"], self.student)

    def test_get_calls_frappe_client(self):
        self.frappe_client.get.return_value = {"name": "EDU-STU-2026-00001"}
        self.repo.get("EDU-STU-2026-00001")
        self.frappe_client.get.assert_called_once_with("Student", "EDU-STU-2026-00001")

    def test_list_calls_frappe_client(self):
        self.frappe_client.list.return_value = []
        self.repo.list()
        self.frappe_client.list.assert_called_once_with("Student")

    def test_delete_calls_frappe_client(self):
        self.repo.delete("EDU-STU-2026-00001")
        self.frappe_client.delete.assert_called_once_with("Student", "EDU-STU-2026-00001")

    def test_create_handles_missing_name_in_response(self):
        self.frappe_client.find.return_value = []
        self.frappe_client.post.return_value = {}
        self.frappe_client.get.return_value = {"year_start_date": "2026-01-01"}
        result = self.repo.create(self.student)
        self.assertEqual(result["student"].student_id, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)


import unittest
from unittest.mock import MagicMock
from app.repositories.student_repository import StudentRepository
from app.models.student import Student, Mark


class TestStudentRepository(unittest.TestCase):

    def setUp(self):
        self.frappe_client = MagicMock()
        self.repo = StudentRepository(client=self.frappe_client)
        self.student = Student(
            student_name="John Doe",
            date_of_birth="15/08/2005",
            father_name="Robert Doe",
            student_class="10th",
            marks=[Mark(subject="Maths", score=92.0)],
            email="john.doe@school.com"
        )

    def test_create_calls_frappe_client_post(self):
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        self.repo.create(self.student)
        self.frappe_client.post.assert_called_once_with("Student", self.student.to_dict(for_frappe=True))

    def test_create_returns_student_with_id(self):
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        result = self.repo.create(self.student)
        self.assertEqual(result.student_id, "EDU-STU-2026-00001")

    def test_create_returns_new_student_instance(self):
        self.frappe_client.post.return_value = {"name": "EDU-STU-2026-00001"}
        result = self.repo.create(self.student)
        self.assertIsNot(result, self.student)

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
        self.frappe_client.post.return_value = {}
        result = self.repo.create(self.student)
        self.assertEqual(result.student_id, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)


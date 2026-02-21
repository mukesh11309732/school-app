import os
import unittest
from dotenv import load_dotenv
from app.models.student import Student
from app.repositories.student_repository import StudentRepository

load_dotenv()


def get_repo() -> StudentRepository:
    return StudentRepository(
        frappe_url=os.environ["FRAPPE_URL"],
        api_key=os.environ["FRAPPE_API_KEY"],
        api_secret=os.environ["FRAPPE_API_SECRET"]
    )


class TestFrappeStudentIntegration(unittest.TestCase):

    def setUp(self):
        self.repo = get_repo()
        self.created_student_id = None

    def tearDown(self):
        """Delete the created student after each test to keep Frappe clean."""
        if self.created_student_id:
            try:
                self.repo.delete(self.created_student_id)
            except Exception:
                pass

    def test_create_student(self):
        student = Student(
            student_name="Test Integration",
            date_of_birth="01/01/2005",
            father_name="Test Father",
            student_class="10th",
            email="test.integration@school.com"
        )

        result = self.repo.create(student)

        self.created_student_id = result.student_id
        self.assertIsNotNone(result.student_id)
        self.assertTrue(result.student_id.startswith("EDU-STU-"))
        print(f"\n[CREATE] Student created: {result.student_id}")

    def test_get_student(self):
        # First create a student
        student = Student(
            student_name="Get Test",
            date_of_birth="02/02/2005",
            father_name="Get Father",
            student_class="9th",
            email="get.test@school.com"
        )
        created = self.repo.create(student)
        self.created_student_id = created.student_id

        # Now fetch it
        fetched = self.repo.get(created.student_id)

        self.assertEqual(fetched.get("name"), created.student_id)
        self.assertEqual(fetched.get("first_name"), "Get")
        self.assertEqual(fetched.get("last_name"), "Test")
        print(f"\n[GET] Student fetched: {fetched.get('name')}")

    def test_list_students(self):
        students = self.repo.list()

        self.assertIsInstance(students, list)
        self.assertGreater(len(students), 0)
        print(f"\n[LIST] Total students: {len(students)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)




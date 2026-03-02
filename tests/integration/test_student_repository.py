import os
import time
import unittest
from dotenv import load_dotenv
from app.models.student import Student, MissingFieldsError, DuplicateStudentError
from app.models.guardian import Guardian
from app.models.program_enrollment import ProgramEnrollment
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository

load_dotenv()


def get_repo() -> StudentRepository:
    client = FrappeClient(
        frappe_url=os.environ["FRAPPE_URL"],
        api_key=os.environ["FRAPPE_API_KEY"],
        api_secret=os.environ["FRAPPE_API_SECRET"]
    )
    return StudentRepository(client)


def make_student(name: str, guardian_name: str = "Test Father") -> Student:
    return Student(
        student_name=name,
        date_of_birth="01/01/2005",
        address="123 Test Street, Test City",
        guardian=Guardian(guardian_name=guardian_name, relation="Father"),
        program_enrollment=ProgramEnrollment(program="Class VIII", academic_year="2026-2027")
    )


class TestStudentRepositoryFrappeIntegration(unittest.TestCase):

    def setUp(self):
        self.repo = get_repo()
        self.created = []  # list of {student_id, guardian_id, enrollment_id}

    def tearDown(self):
        for record in self.created:
            try:
                self.repo.delete_program_enrollment(record["enrollment_id"])
            except Exception:
                pass
            try:
                self.repo.delete(record["student_id"])
            except Exception:
                pass
            try:
                self.repo.delete_guardian(record["guardian_id"])
            except Exception:
                pass

    def test_create_student(self):
        ts = int(time.time())
        result = self.repo.create(make_student(f"Intg{ts}", f"Father{ts}"))
        self.created.append(result)

        self.assertIsNotNone(result["student_id"])
        self.assertTrue(result["student_id"].startswith("EDU-STU-"))
        print(f"\n[CREATE] Student created: {result['student_id']}")

    def test_get_student(self):
        ts = int(time.time())
        result = self.repo.create(make_student(f"Get{ts}", f"GetFather{ts}"))
        self.created.append(result)

        fetched = self.repo.get(result["student_id"])

        self.assertEqual(fetched.get("name"), result["student_id"])
        self.assertEqual(fetched.get("first_name"), f"Get{ts}")
        print(f"\n[GET] Student fetched: {fetched.get('name')}")

    def test_list_students(self):
        students = self.repo.list()

        self.assertIsInstance(students, list)
        self.assertGreater(len(students), 0)
        print(f"\n[LIST] Total students: {len(students)}")

    def test_create_duplicate_student_raises_error(self):
        """Creating a student with same name and guardian should raise DuplicateStudentError."""
        with self.assertRaises(DuplicateStudentError):
            self.repo.create(make_student("Test Integration", "Test Father"))
        print(f"\n[DUPLICATE] Duplicate student correctly rejected")

    def test_create_student_missing_fields_raises_error(self):
        """Validation should raise MissingFieldsError before hitting Frappe."""
        with self.assertRaises(MissingFieldsError) as ctx:
            Student(
                student_name="Incomplete Student",
                date_of_birth="01/01/2005"
                # missing: address, guardian, program_enrollment
            )
        exc = ctx.exception
        self.assertIn("address", exc.missing)
        self.assertIn("guardian", exc.missing)
        self.assertIn("program_enrollment", exc.missing)
        self.assertNotIn("student_class", exc.missing)
        self.assertNotIn("student_id", exc.missing)
        print(f"\n[VALIDATION] Missing fields caught: {exc.missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

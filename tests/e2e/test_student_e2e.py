import os
import unittest
from dotenv import load_dotenv
from app.api.feed_student_data import main
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository

load_dotenv()

OCR_TEXT = """
Student Name: E2E Testuser
Date of Birth: 05/06/2004
Father's Name: E2E Father
Class: 11th Grade

Marks:
Mathematics: 90
Science: 85
English: 78
History: 82
"""



class TestStudentE2E(unittest.TestCase):
    """
    End-to-end test: OCR text -> OpenAI extraction -> Frappe student creation.
    Set E2E_CLEANUP=true to delete the student after the test.
    """

    def setUp(self):
        client = FrappeClient(
            frappe_url=os.environ["FRAPPE_URL"],
            api_key=os.environ["FRAPPE_API_KEY"],
            api_secret=os.environ["FRAPPE_API_SECRET"]
        )
        self.repo = StudentRepository(client)
        self.created_student_id = None

    def tearDown(self):
        """Always clean up created student from Frappe after test."""
        if self.created_student_id:
            try:
                self.repo.delete(self.created_student_id)
                print(f"\n[CLEANUP] Deleted student: {self.created_student_id}")
            except Exception as e:
                print(f"\n[CLEANUP] Failed to delete {self.created_student_id}: {e}")

    def test_ocr_to_frappe_student(self):
        # Step 1: Run full pipeline
        result = main({"ocr_text": OCR_TEXT})

        # Step 2: Assert successful response
        self.assertEqual(result["statusCode"], 200, msg=result.get("body"))

        body = result["body"]
        student_id = body.get("student_id")
        student = body.get("student")

        self.created_student_id = student_id

        # Step 3: Assert student ID was created in Frappe
        self.assertIsNotNone(student_id)
        self.assertTrue(student_id.startswith("EDU-STU-"))
        print(f"\n[E2E] Student created in Frappe: {student_id}")

        # Step 4: Assert extracted data is correct
        self.assertEqual(student["first_name"], "E2E")
        self.assertEqual(student["last_name"], "Testuser")
        self.assertIsNotNone(student["date_of_birth"])
        self.assertIsInstance(student["marks"], list)
        self.assertGreater(len(student["marks"]), 0)
        print(f"[E2E] Extracted {len(student['marks'])} subjects")

        # Step 5: Verify student exists in Frappe
        fetched = self.repo.get(student_id)
        self.assertEqual(fetched.get("name"), student_id)
        self.assertEqual(fetched.get("first_name"), "E2E")
        print(f"[E2E] Verified student in Frappe: {fetched.get('name')}")


if __name__ == "__main__":
    unittest.main(verbosity=2)




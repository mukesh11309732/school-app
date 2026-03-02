import os
import time
import unittest
from dotenv import load_dotenv
from app.api.feed_student_data import StudentFeedService
from app.ai.ai_client import AIClient
from app.ai.prompts import STUDENT_SYSTEM_PROMPT
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository

load_dotenv()

OCR_TEXT = """
Student Name: E2E Testuser
Date of Birth: 05/06/2004
Father Name: E2E Father
Class: 11th Grade
Student ID: STU-E2E-{ts}
Address: 99 E2E Street, Test City
Program: Class VIII
Academic Year: 2026-2027
"""


class TestStudentE2E(unittest.TestCase):

    def setUp(self):
        frappe_client = FrappeClient(
            frappe_url=os.environ["FRAPPE_URL"],
            api_key=os.environ["FRAPPE_API_KEY"],
            api_secret=os.environ["FRAPPE_API_SECRET"]
        )
        self.repo = StudentRepository(frappe_client)
        ai_client = AIClient(client=OpenAIClient(system_prompt=STUDENT_SYSTEM_PROMPT))
        self.service = StudentFeedService(ai_client=ai_client, repo=self.repo)
        self.created = None  # {student_id, guardian_id, enrollment_id}

    def tearDown(self):
        if self.created:
            try:
                self.repo.delete_program_enrollment(self.created["enrollment_id"])
            except Exception:
                pass
            try:
                self.repo.delete(self.created["student_id"])
                print(f"\n[CLEANUP] Deleted student: {self.created['student_id']}")
            except Exception as e:
                print(f"\n[CLEANUP] Failed to delete student: {e}")
            try:
                self.repo.delete_guardian(self.created["guardian_id"])
            except Exception:
                pass

    def test_ocr_to_frappe_student(self):
        ts = int(time.time())
        ocr = OCR_TEXT.replace("{ts}", str(ts)).replace("E2E Testuser", f"E2E User{ts}").replace("E2E Father", f"E2E Dad{ts}")

        # Step 1: feed returns preview for confirmation
        result = self.service.feed(ocr)
        self.assertEqual(result["statusCode"], 280, msg=result.get("body"))
        self.assertEqual(result["body"]["status"], "pending_confirmation")

        preview = result["body"]["preview"]
        self.assertEqual(preview["first_name"], "E2E")
        print(f"\n[E2E] Preview received: {preview['first_name']} {preview['last_name']}")

        # Step 2: confirm creates in Frappe
        confirmed = self.service.confirm(result["body"]["extracted_data"])
        self.assertEqual(confirmed["statusCode"], 200, msg=confirmed.get("body"))

        body = confirmed["body"]
        student_id = body.get("student_id")
        self.created = body.get("created")

        self.assertIsNotNone(student_id)
        self.assertTrue(student_id.startswith("EDU-STU-"))
        print(f"[E2E] Student created in Frappe: {student_id}")

        # Step 3: Verify in Frappe
        fetched = self.repo.get(student_id)
        self.assertEqual(fetched.get("name"), student_id)
        self.assertEqual(fetched.get("first_name"), "E2E")
        print(f"[E2E] Verified in Frappe: {student_id}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

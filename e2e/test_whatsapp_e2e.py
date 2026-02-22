import os
import unittest
from dotenv import load_dotenv
from app.whatsapp.webhook_handler import handle
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository

load_dotenv()

# Simulates a real WhatsApp message payload from Meta
def make_whatsapp_payload(text: str, sender: str = "910000000000") -> dict:
    return {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": sender,
                        "type": "text",
                        "text": {"body": text}
                    }]
                }
            }]
        }]
    }


class TestWhatsAppToFrappeE2E(unittest.TestCase):
    """
    End-to-end test: WhatsApp message -> webhook -> OpenAI -> Frappe student creation.
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

    def test_greeting_does_not_create_student(self):
        payload = make_whatsapp_payload("hello")
        response, status = handle(payload)

        self.assertEqual(status, 200)
        # No student should be created
        self.assertIsNone(self.created_student_id)
        print("\n[E2E] Greeting handled correctly, no student created")

    def test_whatsapp_message_to_frappe_student(self):
        payload = make_whatsapp_payload(
            "John WhatsApp, born 10 March 2006, father Mike WhatsApp, "
            "12th grade, Maths 88, Science 92, English 75"
        )

        response, status = handle(payload)

        self.assertEqual(status, 200)
        print("\n[E2E] Webhook handled successfully")

        # Fetch the latest student from Frappe to verify
        students = self.repo.list()
        self.assertGreater(len(students), 0)

        # Find the created student by name
        latest = self.repo.get(students[0]["name"])
        self.created_student_id = latest.get("name")

        self.assertIsNotNone(self.created_student_id)
        self.assertTrue(self.created_student_id.startswith("EDU-STU-"))
        self.assertEqual(latest.get("first_name"), "John")
        print(f"[E2E] Student verified in Frappe: {self.created_student_id}")


if __name__ == "__main__":
    unittest.main(verbosity=2)


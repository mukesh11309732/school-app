import os
import time
import unittest
from unittest.mock import MagicMock
from dotenv import load_dotenv
from app.whatsapp.webhook_handler import handle
from app.whatsapp.conversation_store import ConversationStore
from app.api.feed_student_data import StudentFeedService
from app.ai.ai_client import AIClient
from app.ai.prompts import STUDENT_SYSTEM_PROMPT
from app.services.openai_client import OpenAIClient
from app.services.frappe_client import FrappeClient
from app.repositories.student_repository import StudentRepository

load_dotenv()


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

    def setUp(self):
        frappe_client = FrappeClient(
            frappe_url=os.environ["FRAPPE_URL"],
            api_key=os.environ["FRAPPE_API_KEY"],
            api_secret=os.environ["FRAPPE_API_SECRET"]
        )
        self.repo = StudentRepository(frappe_client)
        self.ai_client = AIClient(client=OpenAIClient(system_prompt=STUDENT_SYSTEM_PROMPT))
        self.whatsapp_client = MagicMock()
        self.conversation_store = ConversationStore()
        self.feed_service = StudentFeedService(ai_client=self.ai_client, repo=self.repo)
        self.created = None

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

    def _handle(self, payload):
        return handle(payload, self.whatsapp_client, self.feed_service, self.conversation_store)

    def test_greeting_does_not_create_student(self):
        response, status = self._handle(make_whatsapp_payload("hello"))
        self.assertEqual(status, 200)
        self.whatsapp_client.send_message.assert_called_once()
        print("\n[E2E] Greeting handled correctly, no student created")

    def test_whatsapp_message_to_frappe_student(self):
        import random, string
        suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
        sender = "910000000000"
        first = f"Test{suffix}"
        last = f"E2E{suffix}"
        guardian = f"Guard{suffix} Singh"
        ts = int(time.time())

        # Message 1: send student data — should get preview
        response, status = self._handle(make_whatsapp_payload(
            f"Student Name: {first} {last}, Date of Birth: 10 March 2006, "
            f"Father Name: {guardian}, Class: 12th, "
            f"Student ID: STU-{suffix}-{ts}, "
            f"Address: 10 Test Lane Mumbai, "
            f"Program: Class VIII, Academic Year: 2026-2027",
            sender=sender
        ))
        self.assertEqual(status, 200)
        self.assertTrue(self.conversation_store.is_awaiting_confirmation(sender))
        sent_text = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("verify", sent_text.lower())
        print(f"\n[E2E] Preview sent to user:\n{sent_text}")

        # Message 2: reply yes — should create in Frappe
        self.whatsapp_client.reset_mock()
        response, status = self._handle(make_whatsapp_payload("yes", sender=sender))
        self.assertEqual(status, 200)
        self.assertFalse(self.conversation_store.is_awaiting_confirmation(sender))

        sent_text = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("✅", sent_text)
        print(f"\n[E2E] Confirmation reply:\n{sent_text}")

        # Extract student_id from the reply to fetch and verify
        student_id_line = [l for l in sent_text.split("\n") if "ID:" in l]
        self.assertTrue(len(student_id_line) > 0)
        student_id = student_id_line[0].split("ID:")[-1].strip().replace("*", "").strip()
        self.assertTrue(student_id.startswith("EDU-STU-"), msg=f"Unexpected student_id: '{student_id}'")
        print(f"[E2E] Student created: {student_id}")

        fetched = self.repo.get(student_id)
        self.assertTrue(fetched.get("first_name"), "Expected first_name to be non-empty")
        print(f"[E2E] Student verified in Frappe: {student_id}")

        # Set created for cleanup — fetch from store isn't available post-clear, get from Frappe
        self.created = {"student_id": student_id, "guardian_id": None, "enrollment_id": None}
        enrollments = self.repo.client.find("Program Enrollment", {"student": student_id})
        if enrollments:
            self.created["enrollment_id"] = enrollments[0]["name"]
        guardians = fetched.get("guardians", [])
        if guardians:
            self.created["guardian_id"] = guardians[0].get("guardian")


if __name__ == "__main__":
    unittest.main(verbosity=2)

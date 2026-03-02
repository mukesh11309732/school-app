import unittest
from unittest.mock import MagicMock
from app.whatsapp.message_handler import handle_message
from app.whatsapp.constants import HELP_MESSAGE


def make_text_message(text: str, sender: str = "919999999999") -> dict:
    return {"from": sender, "type": "text", "text": {"body": text}}


def make_image_message(sender: str = "919999999999") -> dict:
    return {"from": sender, "type": "image"}


class TestMessageHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = MagicMock()
        self.feed_service = MagicMock()
        self.conversation_store = MagicMock()
        self.conversation_store.is_awaiting_confirmation.return_value = False
        self.conversation_store.get.return_value = None
        self.conversation_store.get_confirmed_data.return_value = {}

    # ...existing code...

    def test_show_details_keyword_returns_entered_details(self):
        self.conversation_store.get_confirmed_data.return_value = {}
        self.conversation_store.get.return_value = {"student_name": "John Doe"}
        for keyword in ["show details", "my details", "details so far"]:
            self.whatsapp_client.reset_mock()
            self._handle(make_text_message(keyword))
            self.whatsapp_client.send_message.assert_called_once()
            self.feed_service.feed.assert_not_called()

    def test_show_details_works_while_awaiting_confirmation(self):
        self.conversation_store.is_awaiting_confirmation.return_value = True
        self.conversation_store.get_confirmed_data.return_value = {"student_name": "John Doe"}
        self._handle(make_text_message("show details"))
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("John Doe", reply)
        self.feed_service.feed.assert_not_called()

    def _handle(self, message):
        return handle_message(message, self.whatsapp_client, self.feed_service, self.conversation_store)

    def test_greeting_sends_help_message(self):
        for greeting in ["hello", "hi", "hey", "Hello", "HI"]:
            self.whatsapp_client.reset_mock()
            self._handle(make_text_message(greeting))
            self.whatsapp_client.send_message.assert_called_once_with("919999999999", HELP_MESSAGE)
            self.feed_service.feed.assert_not_called()

    def test_non_text_message_sends_instruction(self):
        self._handle(make_image_message())
        self.whatsapp_client.send_message.assert_called_once_with(
            "919999999999", "Please send the student data as text."
        )
        self.feed_service.feed.assert_not_called()

    def test_empty_text_sends_instruction(self):
        self._handle(make_text_message("   "))
        self.whatsapp_client.send_message.assert_called_once_with(
            "919999999999", "No text received. Please send student data as text."
        )
        self.feed_service.feed.assert_not_called()

    def test_student_text_calls_feed(self):
        self.feed_service.feed.return_value = {
            "statusCode": 280,
            "body": {
                "status": "pending_confirmation",
                "extracted_data": {
                    "guardian_name": "Robert Doe",
                    "program": "Class X",
                    "academic_year": "2026-2027",
                },
                "preview": {
                    "first_name": "John", "last_name": "Doe",
                    "date_of_birth": "2005-08-15",
                    "address_line_1": "123 Main St",
                }
            }
        }
        self._handle(make_text_message("John Doe, 10th grade"))

        self.feed_service.feed.assert_called_once_with("John Doe, 10th grade", context=None)
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("verify", reply.lower())

    def test_feed_failure_sends_error_message(self):
        self.feed_service.feed.return_value = {
            "statusCode": 500,
            "body": {"error": "OpenAI timeout"}
        }
        self._handle(make_text_message("John Doe, 10th grade"))

        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("⚠️", reply)
        self.assertIn("OpenAI timeout", reply)


if __name__ == "__main__":
    unittest.main(verbosity=2)


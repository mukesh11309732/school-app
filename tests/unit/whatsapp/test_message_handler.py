import unittest
from unittest.mock import MagicMock, call
from app.whatsapp.message_handler import handle_message
from app.whatsapp.constants import HELP_MESSAGE


def make_text_message(text: str, sender: str = "919999999999") -> dict:
    return {"from": sender, "type": "text", "text": {"body": text}}


def make_image_message(sender: str = "919999999999") -> dict:
    return {"from": sender, "type": "image"}


class TestMessageHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = MagicMock()
        self.feed = MagicMock()

    def test_greeting_sends_help_message(self):
        for greeting in ["hello", "hi", "hey", "Hello", "HI"]:
            self.whatsapp_client.reset_mock()
            handle_message(make_text_message(greeting), self.whatsapp_client, self.feed)
            self.whatsapp_client.send_message.assert_called_once_with("919999999999", HELP_MESSAGE)
            self.feed.assert_not_called()

    def test_non_text_message_sends_instruction(self):
        handle_message(make_image_message(), self.whatsapp_client, self.feed)
        self.whatsapp_client.send_message.assert_called_once_with(
            "919999999999", "Please send the student data as text."
        )
        self.feed.assert_not_called()

    def test_empty_text_sends_instruction(self):
        handle_message(make_text_message("   "), self.whatsapp_client, self.feed)
        self.whatsapp_client.send_message.assert_called_once_with(
            "919999999999", "No text received. Please send student data as text."
        )
        self.feed.assert_not_called()

    def test_student_text_calls_feed(self):
        self.feed.return_value = {
            "statusCode": 200,
            "body": {
                "student": {
                    "first_name": "John", "last_name": "Doe",
                    "student_id": "EDU-STU-2026-00001",
                    "class": "10th", "marks": [{"subject": "Maths", "score": 92}]
                }
            }
        }
        handle_message(make_text_message("John Doe, 10th grade"), self.whatsapp_client, self.feed)

        self.feed.assert_called_once_with("John Doe, 10th grade")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("EDU-STU-2026-00001", reply)
        self.assertIn("John Doe", reply)

    def test_feed_failure_sends_error_message(self):
        self.feed.return_value = {
            "statusCode": 500,
            "body": {"error": "OpenAI timeout"}
        }
        handle_message(make_text_message("John Doe, 10th grade"), self.whatsapp_client, self.feed)

        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("Failed", reply)
        self.assertIn("OpenAI timeout", reply)


if __name__ == "__main__":
    unittest.main(verbosity=2)


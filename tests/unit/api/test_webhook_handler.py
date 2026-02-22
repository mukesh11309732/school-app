import unittest
from unittest.mock import MagicMock
from app.whatsapp.webhook_handler import handle


def make_payload(text: str, sender: str = "919999999999") -> dict:
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


class TestWebhookHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = MagicMock()
        self.feed = MagicMock(return_value={
            "statusCode": 200,
            "body": {
                "student": {
                    "first_name": "John", "last_name": "Doe",
                    "student_id": "EDU-STU-2026-00001",
                    "class": "10th", "marks": []
                }
            }
        })

    def test_returns_200_for_valid_message(self):
        response, status = handle(make_payload("John Doe"), self.whatsapp_client, self.feed)
        self.assertEqual(status, 200)

    def test_returns_200_for_empty_messages(self):
        payload = {"entry": [{"changes": [{"value": {"messages": []}}]}]}
        response, status = handle(payload, self.whatsapp_client, self.feed)
        self.assertEqual(status, 200)
        self.assertEqual(response, "No messages")

    def test_returns_500_on_malformed_payload(self):
        response, status = handle({}, self.whatsapp_client, self.feed)
        self.assertEqual(status, 500)

    def test_passes_message_to_handler(self):
        handle(make_payload("John Doe, 10th grade"), self.whatsapp_client, self.feed)
        self.feed.assert_called_once_with("John Doe, 10th grade")


if __name__ == "__main__":
    unittest.main(verbosity=2)


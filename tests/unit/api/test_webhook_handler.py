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
        self.conversation_store = MagicMock()
        self.conversation_store.is_awaiting_confirmation.return_value = False
        self.conversation_store.get.return_value = None
        self.repo = MagicMock()
        self.feed = MagicMock(return_value={
            "statusCode": 280,
            "body": {
                "status": "pending_confirmation",
                "extracted_data": {},
                "preview": {
                    "first_name": "John", "last_name": "Doe",
                    "student_id": "EDU-STU-2026-00001",
                    "class": "10th",
                    "date_of_birth": "", "address_line_1": "",
                }
            }
        })

    def _handle(self, payload):
        return handle(payload, self.whatsapp_client, self.feed, self.conversation_store, self.repo)

    def test_returns_200_for_valid_message(self):
        response, status = self._handle(make_payload("John Doe"))
        self.assertEqual(status, 200)

    def test_returns_200_for_empty_messages(self):
        payload = {"entry": [{"changes": [{"value": {"messages": []}}]}]}
        response, status = self._handle(payload)
        self.assertEqual(status, 200)
        self.assertEqual(response, "No messages")

    def test_returns_500_on_malformed_payload(self):
        response, status = self._handle({})
        self.assertEqual(status, 500)

    def test_passes_message_to_handler(self):
        self._handle(make_payload("John Doe, 10th grade"))
        self.feed.assert_called_once_with("John Doe, 10th grade", context=None)


if __name__ == "__main__":
    unittest.main(verbosity=2)


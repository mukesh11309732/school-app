import unittest
from unittest.mock import MagicMock
from app.whatsapp.handlers.details_handler import handle_show_details

SENDER = "919999999999"


class TestDetailsHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = MagicMock()
        self.conversation_store = MagicMock()

    def _handle(self):
        handle_show_details(SENDER, self.whatsapp_client, self.conversation_store)

    def test_no_data_sends_not_entered_message(self):
        self.conversation_store.get_confirmed_data.return_value = {}
        self.conversation_store.get.return_value = {}
        self._handle()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("No details", reply)

    def test_partial_data_shows_entered_fields(self):
        self.conversation_store.get_confirmed_data.return_value = {}
        self.conversation_store.get.return_value = {
            "student_name": "John Doe",
            "guardian_name": "Robert Doe",
            "address": "123 Main St",
        }
        self._handle()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("John Doe", reply)
        self.assertIn("Robert Doe", reply)
        self.assertIn("123 Main St", reply)

    def test_full_data_shows_all_fields(self):
        self.conversation_store.get_confirmed_data.return_value = {
            "student_name": "John Doe",
            "date_of_birth": "15/08/2005",
            "address": "123 Main St",
            "guardian_name": "Robert Doe",
            "program": "Class X",
            "academic_year": "2026-2027",
        }
        self.conversation_store.get.return_value = {}
        self._handle()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("John Doe", reply)
        self.assertIn("Class X", reply)
        self.assertIn("2026-2027", reply)

    def test_internal_state_key_not_shown(self):
        self.conversation_store.get_confirmed_data.return_value = {
            "student_name": "John Doe",
            "_state": "awaiting_confirmation",
        }
        self.conversation_store.get.return_value = {}
        self._handle()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertNotIn("_state", reply)
        self.assertNotIn("awaiting_confirmation", reply)

    def test_pending_confirmation_data_is_shown(self):
        """show details works even while awaiting confirmation."""
        self.conversation_store.get_confirmed_data.return_value = {
            "student_name": "John Doe",
            "guardian_name": "Robert Doe",
        }
        self.conversation_store.get.return_value = {}
        self._handle()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("John Doe", reply)


if __name__ == "__main__":
    unittest.main(verbosity=2)



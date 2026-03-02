import unittest
from unittest.mock import MagicMock
from app.whatsapp.handlers.student_handler import handle_student


SENDER = "919999999999"

VALID_PREVIEW = {
    "statusCode": 280,
    "body": {
        "status": "pending_confirmation",
        "extracted_data": {"guardian_name": "Robert Doe", "program": "Class X", "academic_year": "2026-2027"},
        "preview": {
            "first_name": "John", "last_name": "Doe",
            "date_of_birth": "2005-08-15", "address_line_1": "123 Main St",
        }
    }
}


class TestStudentHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = MagicMock()
        self.feed_service = MagicMock()
        self.conversation_store = MagicMock()
        self.conversation_store.get.return_value = None

    def _handle(self, text):
        handle_student(SENDER, text, self.whatsapp_client, self.feed_service, self.conversation_store)

    def test_calls_feed_service_with_ocr_and_context(self):
        self.feed_service.feed.return_value = VALID_PREVIEW
        self._handle("John Doe, 10th grade")
        self.feed_service.feed.assert_called_once_with("John Doe, 10th grade", context=None)

    def test_280_sets_pending_confirmation_and_sends_preview(self):
        self.feed_service.feed.return_value = VALID_PREVIEW
        self._handle("John Doe, 10th grade")
        self.conversation_store.set_pending_confirmation.assert_called_once()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("verify", reply.lower())
        self.assertIn("John Doe", reply)

    def test_422_missing_fields_sends_field_list(self):
        self.feed_service.feed.return_value = {
            "statusCode": 422,
            "body": {
                "error": "missing_fields",
                "missing_fields": ["address"],
                "partial_data": {}
            }
        }
        self._handle("John Doe")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("⚠️", reply)
        self.assertIn("Address", reply)

    def test_422_merges_partial_data_into_store(self):
        partial = {"student_name": "John Doe"}
        self.feed_service.feed.return_value = {
            "statusCode": 422,
            "body": {"error": "missing_fields", "missing_fields": ["address"], "partial_data": partial}
        }
        self._handle("John Doe")
        self.conversation_store.merge.assert_called_once_with(SENDER, partial)

    def test_409_duplicate_merges_partial_data_and_prompts_correction(self):
        partial = {"student_name": "John Doe", "guardian_name": "Robert Doe", "address": "123 Main St"}
        self.feed_service.feed.return_value = {
            "statusCode": 409,
            "body": {
                "error": "duplicate_student",
                "message": "Student 'John Doe' with guardian 'Robert Doe' already exists.",
                "partial_data": partial
            }
        }
        self._handle("John Doe, 10th grade")
        self.conversation_store.merge.assert_called_once_with(SENDER, partial)
        self.conversation_store.clear.assert_not_called()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("⚠️", reply)
        self.assertIn("corrected", reply.lower())

    def test_500_sends_error_message(self):
        self.feed_service.feed.return_value = {
            "statusCode": 500,
            "body": {"error": "OpenAI timeout"}
        }
        self._handle("John Doe, 10th grade")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("❌", reply)
        self.assertIn("OpenAI timeout", reply)

    def test_passes_context_from_store(self):
        ctx = {"student_name": "John"}
        self.conversation_store.get.return_value = ctx
        self.feed_service.feed.return_value = VALID_PREVIEW
        self._handle("more details")
        self.feed_service.feed.assert_called_once_with("more details", context=ctx)


if __name__ == "__main__":
    unittest.main(verbosity=2)


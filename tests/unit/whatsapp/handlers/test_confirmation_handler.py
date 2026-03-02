import unittest
from unittest.mock import MagicMock
from app.whatsapp.handlers.confirmation_handler import handle_confirmation


def make_whatsapp_client():
    return MagicMock()


def make_conversation_store(confirmed_data: dict = None):
    store = MagicMock()
    store.get_confirmed_data.return_value = confirmed_data or {}
    return store


def _ok_response():
    return {
        "statusCode": 200,
        "body": {"student": {"first_name": "John", "last_name": "Doe", "student_id": "EDU-001"}}
    }


class TestConfirmationHandler(unittest.TestCase):

    def setUp(self):
        self.whatsapp_client = make_whatsapp_client()
        self.feed_service = MagicMock()
        self.conversation_store = make_conversation_store(confirmed_data={"student_name": "John Doe"})

    def _handle(self, sender, text):
        handle_confirmation(sender, text, self.whatsapp_client, self.feed_service, self.conversation_store)

    def test_yes_calls_confirm_on_feed_service(self):
        self.feed_service.confirm.return_value = _ok_response()
        self._handle("919999999999", "yes")
        self.feed_service.confirm.assert_called_once_with({"student_name": "John Doe"})

    def test_yes_sends_success_message(self):
        self.feed_service.confirm.return_value = _ok_response()
        self._handle("919999999999", "yes")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("✅", reply)
        self.assertIn("EDU-001", reply)

    def test_yes_clears_conversation_on_success(self):
        self.feed_service.confirm.return_value = _ok_response()
        self._handle("919999999999", "yes")
        self.conversation_store.clear.assert_called_once_with("919999999999")

    def test_yes_sends_error_on_confirm_failure_clears_when_not_correctable(self):
        self.feed_service.confirm.return_value = {
            "statusCode": 500,
            "body": {"message": "Something went wrong"}
        }
        self._handle("919999999999", "yes")
        self.conversation_store.clear.assert_called_once_with("919999999999")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("⚠️", reply)
        self.assertIn("Something went wrong", reply)

    def test_yes_keeps_conversation_alive_on_correctable_error(self):
        self.feed_service.confirm.return_value = {
            "statusCode": 500,
            "body": {"message": "Academic Year 2025-2026 not found", "correctable": True}
        }
        self._handle("919999999999", "yes")
        self.conversation_store.revert_to_editing.assert_called_once_with("919999999999")
        self.conversation_store.clear.assert_not_called()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("Academic Year 2025-2026 not found", reply)
        self.assertIn("correct", reply.lower())

    def test_no_cancels_and_clears(self):
        self._handle("919999999999", "no")
        self.conversation_store.clear.assert_called_once_with("919999999999")
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("Cancelled", reply)
        self.feed_service.confirm.assert_not_called()

    def test_unknown_keyword_asks_to_confirm_cancel_or_edit(self):
        self._handle("919999999999", "maybe")
        self.feed_service.confirm.assert_not_called()
        self.conversation_store.clear.assert_not_called()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("yes", reply.lower())
        self.assertIn("no", reply.lower())
        self.assertIn("edit", reply.lower())

    def test_edit_reverts_to_editing_and_prompts(self):
        self._handle("919999999999", "edit")
        self.conversation_store.revert_to_editing.assert_called_once_with("919999999999")
        self.conversation_store.clear.assert_not_called()
        self.feed_service.confirm.assert_not_called()
        reply = self.whatsapp_client.send_message.call_args[0][1]
        self.assertIn("✏️", reply)

    def test_edit_aliases_work(self):
        for keyword in ["change", "update", "correct", "modify"]:
            self.conversation_store.reset_mock()
            self._handle("919999999999", keyword)
            self.conversation_store.revert_to_editing.assert_called_once_with("919999999999")

    def test_confirm_aliases_work(self):
        for keyword in ["confirm", "ok", "okay", "y", "haan", "ha"]:
            self.feed_service.confirm.return_value = _ok_response()
            self.whatsapp_client.reset_mock()
            self._handle("919999999999", keyword)
            self.feed_service.confirm.assert_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)

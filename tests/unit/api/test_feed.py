import json
import unittest
from unittest.mock import MagicMock
from app.api.feed_student_data import StudentFeedService, _parse_frappe_error


VALID_EXTRACTED = {
    "student_name": "John Doe",
    "date_of_birth": "15/08/2005",
    "address": "123 Main St Mumbai",
    "guardian_name": "Robert Doe",
    "guardian_relation": "Father",
    "program": "Class X",
    "academic_year": "2026-2027",
}


class TestFeed(unittest.TestCase):

    def setUp(self):
        self.ai_client = MagicMock()
        self.repo = MagicMock()
        self.service = StudentFeedService(ai_client=self.ai_client, repo=self.repo)

    def test_returns_400_when_ocr_text_missing(self):
        result = self.service.feed("")
        self.assertEqual(result["statusCode"], 400)
        self.ai_client.extract.assert_not_called()
        self.repo.create.assert_not_called()

    def test_returns_280_on_success_with_preview(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo.check_duplicate_by_name.return_value = None

        result = self.service.feed("John Doe, 10th grade")

        self.assertEqual(result["statusCode"], 280)
        self.assertEqual(result["body"]["status"], "pending_confirmation")
        self.assertIn("preview", result["body"])
        self.assertIn("extracted_data", result["body"])

    def test_calls_ai_client_with_ocr_text(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo.check_duplicate_by_name.return_value = None

        self.service.feed("John Doe, 10th grade")

        self.ai_client.extract.assert_called_once_with("John Doe, 10th grade")

    def test_calls_repo_check_duplicate(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo.check_duplicate_by_name.return_value = None

        self.service.feed("John Doe, 10th grade")

        self.repo.check_duplicate_by_name.assert_called_once_with("John Doe", "Robert Doe")

    def test_duplicate_check_happens_even_when_fields_missing(self):
        """Duplicate check runs as soon as name + guardian are present, before full validation."""
        from app.models.student import DuplicateStudentError
        partial = {
            "student_name": "John Doe",
            "guardian_name": "Robert Doe",
            # missing address, program, academic_year
        }
        self.ai_client.extract.return_value = partial
        self.repo.check_duplicate_by_name.side_effect = DuplicateStudentError("John Doe", "Robert Doe")

        result = self.service.feed("John Doe")

        self.assertEqual(result["statusCode"], 409)
        self.assertEqual(result["body"]["error"], "duplicate_student")
        self.assertEqual(result["body"]["partial_data"], partial)

    def test_returns_500_on_exception(self):
        self.ai_client.extract.side_effect = Exception("OpenAI error")

        result = self.service.feed("John Doe, 10th grade")

        self.assertEqual(result["statusCode"], 500)
        self.assertIn("OpenAI error", result["body"]["error"])


class TestParseFrappeError(unittest.TestCase):

    def _make_frappe_error(self, message: str) -> str:
        inner = json.dumps({"message": message, "title": "Message", "indicator": "red", "raise_exception": 1})
        return json.dumps({
            "exc_type": "DoesNotExistError",
            "_server_messages": json.dumps([inner])
        })

    def test_extracts_message_from_nested_frappe_error(self):
        error = self._make_frappe_error("Academic Year 2025-2026 not found")
        self.assertEqual(_parse_frappe_error(error), "Academic Year 2025-2026 not found")

    def test_falls_back_to_raw_string_if_not_json(self):
        self.assertEqual(_parse_frappe_error("plain error"), "plain error")

    def test_confirm_returns_correctable_on_frappe_error(self):
        from unittest.mock import MagicMock
        ai_client = MagicMock()
        repo = MagicMock()
        service = StudentFeedService(ai_client=ai_client, repo=repo)
        repo.create.side_effect = Exception(self._make_frappe_error("Academic Year 2025-2026 not found"))

        data = {
            "student_name": "John Doe", "address": "123 St",
            "guardian_name": "Robert", "guardian_relation": "Father",
            "program": "Class X", "academic_year": "2025-2026"
        }
        result = service.confirm(data)
        self.assertEqual(result["statusCode"], 500)
        self.assertEqual(result["body"]["message"], "Academic Year 2025-2026 not found")
        self.assertTrue(result["body"]["correctable"])


if __name__ == "__main__":
    unittest.main(verbosity=2)


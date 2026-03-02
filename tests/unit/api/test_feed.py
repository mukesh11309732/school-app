import unittest
from unittest.mock import MagicMock
from app.api.feed_student_data import feed


VALID_EXTRACTED = {
    "student_name": "John Doe",
    "date_of_birth": "15/08/2005",
    "student_class": "10th",
    "student_id": "EDU-STU-2026-00001",
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

    def test_returns_400_when_ocr_text_missing(self):
        result = feed("", self.ai_client, self.repo)
        self.assertEqual(result["statusCode"], 400)
        self.ai_client.extract.assert_not_called()
        self.repo.create.assert_not_called()

    def test_returns_280_on_success_with_preview(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo._check_duplicate.return_value = None

        result = feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.assertEqual(result["statusCode"], 280)
        self.assertEqual(result["body"]["status"], "pending_confirmation")
        self.assertIn("preview", result["body"])
        self.assertIn("extracted_data", result["body"])

    def test_calls_ai_client_with_ocr_text(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo._check_duplicate.return_value = None

        feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.ai_client.extract.assert_called_once_with("John Doe, 10th grade")

    def test_calls_repo_check_duplicate(self):
        self.ai_client.extract.return_value = VALID_EXTRACTED
        self.repo._check_duplicate.return_value = None

        feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.repo._check_duplicate.assert_called_once()

    def test_returns_500_on_exception(self):
        self.ai_client.extract.side_effect = Exception("OpenAI error")

        result = feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.assertEqual(result["statusCode"], 500)
        self.assertIn("OpenAI error", result["body"]["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)



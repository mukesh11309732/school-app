import unittest
from unittest.mock import MagicMock
from app.api.feed_student_data import feed
from app.models.student import Student, Mark


def make_student(**kwargs) -> Student:
    defaults = dict(
        student_name="John Doe",
        date_of_birth="15/08/2005",
        father_name="Robert Doe",
        student_class="10th",
        marks=[Mark(subject="Maths", score=92)],
        email="john.doe@school.com",
        student_id="EDU-STU-2026-00001"
    )
    return Student(**{**defaults, **kwargs})


class TestFeed(unittest.TestCase):

    def setUp(self):
        self.ai_client = MagicMock()
        self.repo = MagicMock()

    def test_returns_400_when_ocr_text_missing(self):
        result = feed("", self.ai_client, self.repo)
        self.assertEqual(result["statusCode"], 400)
        self.ai_client.process.assert_not_called()
        self.repo.create.assert_not_called()

    def test_returns_200_on_success(self):
        student = make_student()
        self.ai_client.process.return_value = student
        self.repo.create.return_value = student

        result = feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result["body"]["student_id"], "EDU-STU-2026-00001")
        self.assertEqual(result["body"]["student"]["first_name"], "John")

    def test_calls_ai_client_with_ocr_text(self):
        student = make_student()
        self.ai_client.process.return_value = student
        self.repo.create.return_value = student

        feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.ai_client.process.assert_called_once_with("John Doe, 10th grade")

    def test_calls_repo_create_with_student(self):
        student = make_student()
        self.ai_client.process.return_value = student
        self.repo.create.return_value = student

        feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.repo.create.assert_called_once_with(student)

    def test_returns_500_on_exception(self):
        self.ai_client.process.side_effect = Exception("OpenAI error")

        result = feed("John Doe, 10th grade", self.ai_client, self.repo)

        self.assertEqual(result["statusCode"], 500)
        self.assertIn("OpenAI error", result["body"]["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)



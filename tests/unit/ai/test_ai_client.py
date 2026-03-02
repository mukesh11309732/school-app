import unittest
from unittest.mock import MagicMock
from app.ai.ai_client import AIClient
from app.models.student import Student, Mark
from app.models.guardian import Guardian
from app.models.program_enrollment import ProgramEnrollment


def make_full_student(**kwargs):
    defaults = dict(
        student_name="John Doe",
        date_of_birth="15/08/2005",
        address="123 Main St Mumbai",
        guardian=Guardian(guardian_name="Robert Doe"),
        program_enrollment=ProgramEnrollment(program="Class X", academic_year="2026-2027"),
        marks=[Mark(subject="Maths", score=92.0)],
        email="john.doe@school.com",
    )
    return Student(**{**defaults, **kwargs})


class TestAIClient(unittest.TestCase):

    def setUp(self):
        self.openai_client = MagicMock()
        self.ai_client = AIClient(client=self.openai_client)
        self.student = make_full_student()

    def test_process_calls_openai_client_with_schema(self):
        self.openai_client.process.return_value = self.student
        self.ai_client.process("some ocr text")
        self.openai_client.process.assert_called_once_with("some ocr text", Student)

    def test_process_returns_student(self):
        self.openai_client.process.return_value = self.student
        result = self.ai_client.process("some ocr text")
        self.assertIsInstance(result, Student)
        self.assertEqual(result.student_name, "John Doe")

    def test_process_propagates_exception(self):
        self.openai_client.process.side_effect = Exception("API error")
        with self.assertRaises(Exception) as ctx:
            self.ai_client.process("some ocr text")
        self.assertIn("API error", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)

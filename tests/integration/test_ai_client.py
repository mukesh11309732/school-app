import unittest
from dotenv import load_dotenv
from app.ai.ai_client import AIClient
from app.ai.prompts import STUDENT_SYSTEM_PROMPT
from app.services.openai_client import OpenAIClient

load_dotenv()

OCR_TEXT = (
    "Student Name: John Doe\n"
    "Date of Birth: 15/08/2005\n"
    "Father Name: Robert Doe\n"
    "Class: 10th\n"
    "Student ID: STU-JD-001\n"
    "Address: 12 Baker Street, Mumbai\n"
    "Program: Class VIII\n"
    "Academic Year: 2026-2027\n"
    "Maths: 92, Science: 88"
)


class TestAIClientOpenAIIntegration(unittest.TestCase):

    def setUp(self):
        self.client = AIClient(client=OpenAIClient(system_prompt=STUDENT_SYSTEM_PROMPT))

    def test_returns_dict(self):
        result = self.client.extract(OCR_TEXT)
        self.assertIsInstance(result, dict)
        print(f"\n[AI] Extracted dict: {result}")

    def test_student_name_extracted(self):
        result = self.client.extract(OCR_TEXT)
        self.assertEqual(result.get("student_name"), "John Doe")

    def test_date_of_birth_extracted(self):
        result = self.client.extract(OCR_TEXT)
        self.assertIsNotNone(result.get("date_of_birth"))

    def test_guardian_name_extracted(self):
        result = self.client.extract(OCR_TEXT)
        self.assertEqual(result.get("guardian_name"), "Robert Doe")

    def test_program_extracted(self):
        result = self.client.extract(OCR_TEXT)
        self.assertIsNotNone(result.get("program"))

    def test_address_extracted(self):
        result = self.client.extract(OCR_TEXT)
        self.assertIsNotNone(result.get("address"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

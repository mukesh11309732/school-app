import unittest
from dotenv import load_dotenv
from app.ai.ai_client import AIClient
from app.services.openai_client import OpenAIClient
from app.models.student import Student

load_dotenv()

OCR_TEXT = "Student Name: John Doe\nDate of Birth: 15/08/2005\nFather Name: Robert Doe\nClass: 10th\nMaths: 92, Science: 88"


class TestAIClientOpenAIIntegration(unittest.TestCase):

    def setUp(self):
        self.client = AIClient(client=OpenAIClient())

    def test_returns_student_instance(self):
        result = self.client.process(OCR_TEXT)
        self.assertIsInstance(result, Student)
        print(f"\n[AI] Returned Student instance: {result.student_name}")

    def test_student_name_extracted(self):
        result = self.client.process(OCR_TEXT)
        self.assertEqual(result.student_name, "John Doe")

    def test_date_of_birth_extracted(self):
        result = self.client.process(OCR_TEXT)
        self.assertEqual(result.date_of_birth, "15/08/2005")

    def test_father_name_extracted(self):
        result = self.client.process(OCR_TEXT)
        self.assertEqual(result.father_name, "Robert Doe")

    def test_marks_extracted(self):
        result = self.client.process(OCR_TEXT)
        self.assertGreater(len(result.marks), 0)
        subjects = [m.subject for m in result.marks]
        self.assertIn("Maths", subjects)
        self.assertIn("Science", subjects)

    def test_email_generated(self):
        result = self.client.process(OCR_TEXT)
        self.assertIn("john.doe", result.email)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import unittest
from app.models.student import Student, Mark, _format_date


class TestFormatDate(unittest.TestCase):

    def test_converts_dd_mm_yyyy_to_yyyy_mm_dd(self):
        self.assertEqual(_format_date("15/08/2005"), "2005-08-15")

    def test_returns_original_if_invalid(self):
        self.assertEqual(_format_date("2005-08-15"), "2005-08-15")

    def test_returns_original_if_empty(self):
        self.assertEqual(_format_date(""), "")


class TestMark(unittest.TestCase):

    def test_to_dict(self):
        mark = Mark(subject="Maths", score=92.0)
        self.assertEqual(mark.to_dict(), {"subject": "Maths", "score": 92.0})


class TestStudent(unittest.TestCase):

    def setUp(self):
        self.student = Student(
            student_name="John Doe",
            date_of_birth="15/08/2005",
            father_name="Robert Doe",
            student_class="10th",
            marks=[Mark(subject="Maths", score=92.0)],
            email="john.doe@school.com",
            student_id="EDU-STU-2026-00001"
        )

    def test_first_name(self):
        self.assertEqual(self.student.first_name, "John")

    def test_last_name(self):
        self.assertEqual(self.student.last_name, "Doe")

    def test_first_name_single_word(self):
        s = Student(student_name="John", date_of_birth="", father_name="", student_class="")
        self.assertEqual(s.first_name, "John")
        self.assertEqual(s.last_name, "")

    def test_with_email_generates_email(self):
        s = Student(student_name="John Doe", date_of_birth="", father_name="", student_class="")
        result = s.with_email()
        self.assertIn("john.doe", result.email)
        self.assertIn("@school.com", result.email)

    def test_with_email_returns_new_instance(self):
        s = Student(student_name="John Doe", date_of_birth="", father_name="", student_class="")
        result = s.with_email()
        self.assertIsNot(result, s)

    def test_to_dict(self):
        d = self.student.to_dict()
        self.assertEqual(d["first_name"], "John")
        self.assertEqual(d["last_name"], "Doe")
        self.assertEqual(d["class"], "10th")
        self.assertEqual(d["date_of_birth"], "15/08/2005")
        self.assertEqual(len(d["marks"]), 1)

    def test_to_dict_for_frappe(self):
        d = self.student.to_dict(for_frappe=True)
        self.assertEqual(d["doctype"], "Student")
        self.assertEqual(d["student_email_id"], "john.doe@school.com")
        self.assertEqual(d["guardian_name"], "Robert Doe")
        self.assertEqual(d["date_of_birth"], "2005-08-15")
        self.assertNotIn("marks", d)
        self.assertNotIn("class", d)
        self.assertNotIn("student_id", d)
        self.assertNotIn("email", d)
        self.assertNotIn("father_name", d)


if __name__ == "__main__":
    unittest.main(verbosity=2)


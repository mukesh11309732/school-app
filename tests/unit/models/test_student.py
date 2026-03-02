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


def make_full_student(**kwargs):
    from app.models.guardian import Guardian
    from app.models.program_enrollment import ProgramEnrollment
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


class TestStudent(unittest.TestCase):

    def setUp(self):
        self.student = make_full_student()

    def test_first_name(self):
        self.assertEqual(self.student.first_name, "John")

    def test_last_name(self):
        self.assertEqual(self.student.last_name, "Doe")

    def test_first_name_single_word(self):
        s = make_full_student(student_name="John")
        self.assertEqual(s.first_name, "John")
        self.assertEqual(s.last_name, "")

    def test_with_email_generates_email(self):
        s = make_full_student(student_name="John Doe", email="")
        result = s.with_email()
        self.assertIn("john.doe", result.email)
        self.assertIn("@school.com", result.email)
        self.assertNotIn("..", result.email)

    def test_with_email_single_name_no_double_dot(self):
        s = make_full_student(student_name="Mukesh", email="")
        result = s.with_email()
        self.assertIn("mukesh", result.email)
        self.assertIn("@school.com", result.email)
        self.assertNotIn("..", result.email)

    def test_with_email_returns_new_instance(self):
        s = make_full_student(student_name="John Doe", email="")
        result = s.with_email()
        self.assertIsNot(result, s)

    def test_to_dict(self):
        d = self.student.to_dict()
        self.assertEqual(d["first_name"], "John")
        self.assertEqual(d["last_name"], "Doe")
        self.assertNotIn("marks", d)
        self.assertNotIn("email", d)

    def test_to_dict_for_frappe(self):
        d = self.student.to_dict()
        self.assertEqual(d["doctype"], "Student")
        self.assertEqual(d["student_email_id"], "john.doe@school.com")
        self.assertEqual(d["date_of_birth"], "2005-08-15")
        self.assertEqual(d["address_line_1"], "123 Main St Mumbai")
        self.assertNotIn("marks", d)
        self.assertNotIn("email", d)
        self.assertNotIn("class", d)
        self.assertNotIn("student_id", d)


if __name__ == "__main__":
    unittest.main(verbosity=2)

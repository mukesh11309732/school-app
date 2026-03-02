from pydantic import BaseModel
class ProgramEnrollment(BaseModel):
    program: str
    academic_year: str
    enrollment_date: str = ""
    def to_dict(self) -> dict:
        return {
            "doctype": "Program Enrollment",
            "program": self.program,
            "academic_year": self.academic_year,
            "enrollment_date": self.enrollment_date,
        }

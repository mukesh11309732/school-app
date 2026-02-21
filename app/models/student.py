from typing import List
import time
from pydantic import BaseModel, Field


def _format_date(date_str: str) -> str:
    """Converts DD/MM/YYYY to YYYY-MM-DD for Frappe."""
    try:
        parts = date_str.split("/")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except Exception:
        pass
    return date_str


class Mark(BaseModel):
    subject: str
    score: float

    def to_dict(self) -> dict:
        return {"subject": self.subject, "score": self.score}


class Student(BaseModel):
    student_name: str
    date_of_birth: str
    father_name: str
    student_class: str
    marks: List[Mark] = Field(default_factory=list)
    email: str = ""
    student_id: str = ""

    @property
    def first_name(self) -> str:
        return self.student_name.split()[0] if self.student_name else "Unknown"

    @property
    def last_name(self) -> str:
        parts = self.student_name.split()
        return " ".join(parts[1:]) if len(parts) > 1 else ""

    def with_email(self) -> "Student":
        """Returns a new Student with a unique generated email."""
        email = f"{self.first_name.lower()}.{self.last_name.lower()}.{int(time.time())}@school.com".replace(" ", "")
        return self.model_copy(update={"email": email})

    def to_dict(self, for_frappe: bool = False) -> dict:
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "date_of_birth": _format_date(self.date_of_birth) if for_frappe else self.date_of_birth,
            "father_name": self.father_name,
            "class": self.student_class,
            "marks": [m.to_dict() for m in self.marks],
            "student_id": self.student_id
        }
        if for_frappe:
            data["doctype"] = "Student"
            data["student_email_id"] = data.pop("email")
            data["guardian_name"] = data.pop("father_name")
            data.pop("marks")
            data.pop("class")
            data.pop("student_id")
        return data


from typing import List, Optional
import time
from pydantic import BaseModel, Field, model_validator

from app.models.guardian import Guardian
from app.models.program_enrollment import ProgramEnrollment


def _format_date(date_str: str) -> str:
    """Converts DD/MM/YYYY to YYYY-MM-DD for Frappe."""
    try:
        parts = date_str.split("/")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except Exception:
        pass
    return date_str


MANDATORY_FIELDS = ["student_name", "address", "student_id", "student_class", "guardian", "program_enrollment"]


class MissingFieldsError(Exception):
    """Raised when mandatory student fields are missing."""
    def __init__(self, missing: list):
        self.missing = missing
        super().__init__(f"Missing mandatory fields: {', '.join(missing)}")


class DuplicateStudentError(Exception):
    """Raised when a student with the same name and father name already exists."""
    def __init__(self, student_name: str, guardian_name: str):
        super().__init__(f"Student '{student_name}' with guardian '{guardian_name}' already exists.")


class Mark(BaseModel):
    subject: str
    score: float

    def to_dict(self) -> dict:
        return {"subject": self.subject, "score": self.score}


class Student(BaseModel):
    student_name: str = ""
    date_of_birth: str = ""
    student_class: str = ""
    student_id: str = ""
    address: str = ""
    guardian: Optional[Guardian] = None
    program_enrollment: Optional[ProgramEnrollment] = None
    marks: List[Mark] = Field(default_factory=list)
    email: str = ""

    @model_validator(mode="after")
    def validate_mandatory_fields(self) -> "Student":
        missing = []
        for field in MANDATORY_FIELDS:
            value = getattr(self, field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        if missing:
            raise MissingFieldsError(missing)
        return self

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

    def _generated_email(self) -> str:
        """Generates a unique email if not provided."""
        if self.email:
            return self.email
        name = f"{self.first_name}.{self.last_name}".lower().replace(" ", "")
        return f"{name}.{int(time.time())}@school.com"

    def to_dict(self) -> dict:
        return {
            "doctype": "Student",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": _format_date(self.date_of_birth),
            "student_email_id": self._generated_email(),
            "address_line_1": self.address,
            "student_id": self.student_id,
            "class": self.student_class,
        }


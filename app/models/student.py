from typing import List, Optional
from dataclasses import dataclass
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


@dataclass
class StudentFieldMeta:
    key: str            # flat dict key used in extracted data / conversation store
    label: str          # human-readable label shown to user
    prompt_hint: str    # description used in the AI system prompt
    mandatory: bool = False
    model_field: str = None  # Student model attribute name; None if not directly on Student
    hint: str = None    # extra guidance shown to user when this field is missing


# Single source of truth — add/remove fields here only
STUDENT_FIELDS: list[StudentFieldMeta] = [
    StudentFieldMeta("student_name",      "Full Name",            "student_name (full name)",                                     mandatory=True,  model_field="student_name"),
    StudentFieldMeta("date_of_birth",     "Date of Birth",        "date_of_birth (DD/MM/YYYY)",                                                    model_field="date_of_birth",    hint="e.g. 15 August 2005"),
    StudentFieldMeta("address",           "Address",              "address",                                                      mandatory=True,  model_field="address"),
    StudentFieldMeta("guardian_name",     "Father/Guardian Name", "guardian_name (father or guardian full name)",                 mandatory=True,  model_field="guardian"),
    StudentFieldMeta("guardian_relation", "Guardian Relation",    "guardian_relation (Father, Mother, Guardian — default Father)"),
    StudentFieldMeta("program",           "Program",              "program (academic program name, e.g. Class VIII)",             mandatory=True,  model_field="program_enrollment", hint="e.g. Class VIII, Class X"),
    StudentFieldMeta("academic_year",     "Academic Year",        "academic_year (e.g. 2026-2027)",                               mandatory=True,  model_field="program_enrollment", hint="e.g. 2025-2026"),
]

# Derived — no need to edit these
# Unique model fields that are mandatory (deduplicated, preserving order)
_seen = set()
MANDATORY_FIELDS = [
    f.model_field for f in STUDENT_FIELDS
    if f.mandatory and f.model_field and not (f.model_field in _seen or _seen.add(f.model_field))
]
# Flat keys that must be present before constructing the Student model
MANDATORY_FLAT_KEYS: list[str] = [f.key for f in STUDENT_FIELDS if f.mandatory]
FIELD_LABELS: dict[str, str] = {f.key: f.label for f in STUDENT_FIELDS}
FIELD_HINTS: dict[str, str] = {f.key: f.hint for f in STUDENT_FIELDS if f.hint}
FIELD_DISPLAY: list[tuple[str, str]] = [(f.key, f.label) for f in STUDENT_FIELDS]
PROMPT_FIELDS: list[str] = [f.prompt_hint for f in STUDENT_FIELDS]


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

    def _email_prefix(self) -> str:
        """Builds a clean email prefix from the student name, no double dots."""
        parts = [p for p in [self.first_name.lower(), self.last_name.lower()] if p]
        return ".".join(parts).replace(" ", "")

    def with_email(self) -> "Student":
        """Returns a new Student with a unique generated email."""
        email = f"{self._email_prefix()}.{int(time.time())}@school.com"
        return self.model_copy(update={"email": email})

    def _generated_email(self) -> str:
        """Returns the stored email or generates a unique one."""
        if self.email:
            return self.email
        return f"{self._email_prefix()}.{int(time.time())}@school.com"

    def to_dict(self) -> dict:
        return {
            "doctype": "Student",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": _format_date(self.date_of_birth),
            "student_email_id": self._generated_email(),
            "address_line_1": self.address,
        }


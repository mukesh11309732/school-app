from dataclasses import dataclass, field
from typing import List


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
class Mark:
    subject: str
    score: float

    @staticmethod
    def from_dict(data: dict) -> "Mark":
        return Mark(
            subject=data.get("subject", ""),
            score=data.get("score", 0)
        )

    def to_dict(self) -> dict:
        return {"subject": self.subject, "score": self.score}


@dataclass
class Student:
    first_name: str
    last_name: str
    date_of_birth: str
    father_name: str
    student_class: str
    marks: List[Mark] = field(default_factory=list)
    email: str = ""
    student_id: str = ""

    @staticmethod
    def from_ocr_dict(data: dict) -> "Student":
        """Creates a Student instance from OpenAI extracted OCR data."""
        name_parts = data.get("student_name", "").split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        email = f"{first_name.lower()}.{last_name.lower()}@school.com".replace(" ", "")

        return Student(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=data.get("date_of_birth", ""),
            father_name=data.get("father_name", ""),
            student_class=data.get("class", ""),
            marks=[Mark.from_dict(m) for m in data.get("marks", [])],
            email=email
        )

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


from pydantic import BaseModel


class Guardian(BaseModel):
    guardian_name: str
    relation: str = "Father"

    def to_dict(self) -> dict:
        return {
            "doctype": "Guardian",
            "guardian_name": self.guardian_name,
            "relation": self.relation,
        }



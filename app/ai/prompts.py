from app.models.student import PROMPT_FIELDS

STUDENT_SYSTEM_PROMPT = (
    "You are an assistant that extracts structured student data from text and returns JSON.\n"
    "Always use these exact field names:\n"
    + "".join(f"- {hint}\n" for hint in PROMPT_FIELDS)
    + "Return only the flat JSON object with these keys. Do not nest under any parent key."
)

import requests


def create_student(frappe_url, api_key, api_secret, student_data):
    """
    Creates a Student record in Frappe Education using the REST API.

    student_data expected format:
    {
        "student_name": "John Doe",
        "date_of_birth": "15/08/2005",
        "father_name": "Robert Doe",
        "class": "10th Grade",
        "marks": [{"subject": "Maths", "score": 92}, ...]
    }
    """
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    # Create Student document
    student_payload = {
        "doctype": "Student",
        "first_name": student_data.get("student_name", "").split()[0],
        "last_name": " ".join(student_data.get("student_name", "").split()[1:]),
        "date_of_birth": _format_date(student_data.get("date_of_birth", "")),
        "guardian_name": student_data.get("father_name", ""),
    }

    response = requests.post(
        f"{frappe_url}/api/resource/Student",
        json=student_payload,
        headers=headers
    )

    if response.status_code not in (200, 201):
        return {"statusCode": response.status_code, "body": {"error": response.text}}

    student_doc = response.json().get("data", {})
    student_id = student_doc.get("name")

    return {
        "statusCode": 200,
        "body": {
            "student_id": student_id,
            "student": student_doc
        }
    }


def _format_date(date_str):
    """Converts DD/MM/YYYY to YYYY-MM-DD for Frappe."""
    try:
        parts = date_str.split("/")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except Exception:
        pass
    return date_str


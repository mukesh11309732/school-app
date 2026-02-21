import os
from app.services.openai_client import extract_student_data
from app.services.frappe_client import create_student
from app.extract_student_data import get_api_key, get_ocr_text


def get_frappe_config(args):
    """Retrieves Frappe connection config from args or environment variables."""
    return {
        "frappe_url": args.get("FRAPPE_URL") or os.environ.get("FRAPPE_URL"),
        "api_key": args.get("FRAPPE_API_KEY") or os.environ.get("FRAPPE_API_KEY"),
        "api_secret": args.get("FRAPPE_API_SECRET") or os.environ.get("FRAPPE_API_SECRET"),
    }


def main(args):
    # Step 1: Get OCR text
    api_key = get_api_key(args)
    if not api_key:
        return {"statusCode": 500, "body": {"error": "OPENAI_API_KEY is not set"}}

    ocr_text, error = get_ocr_text(args)
    if error:
        return error
    if not ocr_text:
        return {"statusCode": 400, "body": {"error": "Missing required parameter: ocr_text or file_path"}}

    # Step 2: Get Frappe config
    config = get_frappe_config(args)
    if not all(config.values()):
        return {"statusCode": 500, "body": {"error": "Missing Frappe config: FRAPPE_URL, FRAPPE_API_KEY, FRAPPE_API_SECRET"}}

    try:
        # Step 3: Extract Student object directly from OCR
        student = extract_student_data(ocr_text, api_key)

        # Step 4: Feed Student into Frappe
        result = create_student(
            frappe_url=config["frappe_url"],
            api_key=config["api_key"],
            api_secret=config["api_secret"],
            student=student
        )
        return result
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}


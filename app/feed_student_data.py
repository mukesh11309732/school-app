import os
from app.extract_student_data import main as extract_main
from app.services.frappe_client import create_student


def get_frappe_config(args):
    """Retrieves Frappe connection config from args or environment variables."""
    return {
        "frappe_url": args.get("FRAPPE_URL") or os.environ.get("FRAPPE_URL"),
        "api_key": args.get("FRAPPE_API_KEY") or os.environ.get("FRAPPE_API_KEY"),
        "api_secret": args.get("FRAPPE_API_SECRET") or os.environ.get("FRAPPE_API_SECRET"),
    }


def main(args):
    # Step 1: Extract student data from OCR
    extract_result = extract_main(args)
    if extract_result.get("statusCode") != 200:
        return extract_result

    student_data = extract_result["body"]["student_data"]

    # Step 2: Get Frappe config
    config = get_frappe_config(args)
    if not all(config.values()):
        return {
            "statusCode": 500,
            "body": {"error": "Missing Frappe config: FRAPPE_URL, FRAPPE_API_KEY, FRAPPE_API_SECRET"}
        }

    # Step 3: Feed student data into Frappe
    result = create_student(
        frappe_url=config["frappe_url"],
        api_key=config["api_key"],
        api_secret=config["api_secret"],
        student_data=student_data
    )

    return result


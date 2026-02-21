import os
from app.utils.file_reader import read_ocr_file
from app.services.openai_client import extract_student_data


def get_api_key(args):
    """Retrieves the API key from args or environment variables."""
    return args.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")


def get_ocr_text(args):
    """Resolves OCR text from direct input or file path."""
    file_path = args.get("file_path", "")
    if file_path:
        return read_ocr_file(file_path)
    return args.get("ocr_text", ""), None


def main(args):
    api_key = get_api_key(args)
    if not api_key:
        return {"statusCode": 500, "body": {"error": "OPENAI_API_KEY is not set"}}

    ocr_text, error = get_ocr_text(args)
    if error:
        return error
    if not ocr_text:
        return {"statusCode": 400, "body": {"error": "Missing required parameter: ocr_text or file_path"}}

    try:
        student = extract_student_data(ocr_text, api_key)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"student_data": student.to_dict()}
        }
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}



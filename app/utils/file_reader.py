def read_ocr_file(file_path):
    """Reads OCR text from a given file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), None
    except FileNotFoundError:
        return None, {"statusCode": 404, "body": {"error": f"File not found: {file_path}"}}
    except Exception as e:
        return None, {"statusCode": 500, "body": {"error": f"Error reading file: {str(e)}"}}


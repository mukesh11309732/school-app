import json
from dotenv import load_dotenv
from app.extract_student_data import main

load_dotenv()

args = {
    "file_path": "data/sample_ocr.txt"
}

result = main(args)
print("Status Code:", result["statusCode"])
print("Response:")
print(json.dumps(result["body"], indent=2))





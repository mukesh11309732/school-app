# School App

A Python app that extracts structured student data from OCR text using OpenAI and feeds it into Frappe Education.

## Project Structure

```
school-app/
├── app/
│   ├── ai/
│   │   └── ai_client.py            # AIClient — wraps OpenAIClient
│   ├── models/
│   │   └── student.py              # Student & Mark Pydantic models
│   ├── repositories/
│   │   └── student_repository.py   # StudentRepository — CRUD via FrappeClient
│   └── services/
│       ├── openai_client.py        # OpenAIClient — calls OpenAI API
│       └── frappe_client.py        # FrappeClient — calls Frappe REST API
├── tests/
│   ├── test_ai_client.py           # AIClient + OpenAI integration tests
│   └── test_student_repository.py  # StudentRepository + Frappe integration tests
├── e2e/
│   └── test_student_e2e.py         # End-to-end: OCR → OpenAI → Frappe
├── server.py                       # HTTP server with /feed endpoint
└── requirements.txt
```

## Setup

1. Clone the repo and install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
FRAPPE_URL=https://your-site.frappe.cloud
FRAPPE_API_KEY=your-frappe-api-key
FRAPPE_API_SECRET=your-frappe-api-secret
```

## Running the Server

```bash
PORT=8080 python server.py
```

## API

### `POST /feed`
Extracts student data from OCR text and creates a Student record in Frappe Education.

**Request:**
```json
{
  "ocr_text": "Student Name: John Doe\nDate of Birth: 15/08/2005\nFather Name: Robert Doe\nClass: 10th\nMaths: 92, Science: 88"
}
```

**curl:**
```bash
curl -X POST http://localhost:8080/feed \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "Student Name: John Doe\nDate of Birth: 15/08/2005\nFather Name: Robert Doe\nClass: 10th\nMaths: 92, Science: 88"}'
```

**Response:**
```json
{
  "student_id": "EDU-STU-2026-00001",
  "student": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe.1234567890@school.com",
    "date_of_birth": "15/08/2005",
    "father_name": "Robert Doe",
    "class": "10th",
    "marks": [
      { "subject": "Maths", "score": 92 },
      { "subject": "Science", "score": 88 }
    ],
    "student_id": "EDU-STU-2026-00001"
  }
}
```

## Testing

Run all tests:
```bash
python -m unittest discover -v
```

Run specific test suites:
```bash
# AI Client + OpenAI integration
python -m unittest tests.test_ai_client -v

# Student Repository + Frappe integration
python -m unittest tests.test_student_repository -v

# End-to-end
python -m unittest e2e.test_student_e2e -v
```

## Deployment

Deployed on [DigitalOcean App Platform](https://cloud.digitalocean.com/apps). Auto-deploys on push to `main`.

Set the following environment variables in DigitalOcean App Settings:
- `OPENAI_API_KEY`
- `FRAPPE_URL`
- `FRAPPE_API_KEY`
- `FRAPPE_API_SECRET`

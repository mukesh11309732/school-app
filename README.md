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

## WhatsApp Chatbot

Send student OCR text via WhatsApp and the bot will extract and feed it into Frappe automatically.

### Setup

1. Create a [Meta Developer App](https://developers.facebook.com/) and add the WhatsApp product
2. Get your **WhatsApp Token**, **Phone Number ID** and set a **Verify Token**
3. Add to `.env`:
```
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=your-verify-token
```
4. Expose your local server using ngrok:
```bash
ngrok http 8080
```
5. Set the webhook URL in Meta Developer Console to:
```
https://<ngrok-id>.ngrok.io/webhook
```

### Webhook Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/webhook` | Meta verification handshake |
| `POST` | `/webhook` | Receives WhatsApp messages |

### Usage

Simply send a WhatsApp message to your bot number with student data:
```
Student Name: John Doe
Date of Birth: 15/08/2005
Father Name: Robert Doe
Class: 10th
Maths: 92, Science: 88
```

The bot will reply:
```
✅ Student created successfully!
Name: John Doe
ID: EDU-STU-2026-00001
Class: 10th
Subjects: 2
```

## Deployment

Deployed on [DigitalOcean App Platform](https://cloud.digitalocean.com/apps). Auto-deploys on push to `main`.

Set the following environment variables in DigitalOcean App Settings:
- `OPENAI_API_KEY`
- `FRAPPE_URL`
- `FRAPPE_API_KEY`
- `FRAPPE_API_SECRET`

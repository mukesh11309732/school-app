# School AI

A Python-based AI assistant that extracts structured student data from WhatsApp messages and feeds it into [Frappe Education](https://frappe.io/education) automatically.

## Project Structure

```
school-app/
├── app/
│   ├── ai/
│   │   ├── ai_client.py                    # AIClient — wraps OpenAIClient
│   │   └── prompts.py                      # AI system prompt (auto-generated from STUDENT_FIELDS)
│   ├── api/
│   │   ├── feed_student_data.py            # StudentFeedService — extract, validate, confirm
│   │   └── webhook.py                      # WhatsApp webhook entry point
│   ├── models/
│   │   ├── student.py                      # Student model + STUDENT_FIELDS registry (single source of truth)
│   │   ├── guardian.py                     # Guardian model
│   │   └── program_enrollment.py           # ProgramEnrollment model
│   ├── modules/
│   │   └── container.py                    # DI Container
│   ├── repositories/
│   │   └── student_repository.py           # StudentRepository — CRUD via FrappeClient
│   ├── services/
│   │   ├── openai_client.py                # OpenAIClient — calls OpenAI API
│   │   ├── frappe_client.py                # FrappeClient — calls Frappe REST API
│   │   └── whatsapp_client.py              # WhatsAppClient — calls WhatsApp API
│   └── whatsapp/
│       ├── constants.py                    # Keywords, help message
│       ├── conversation_store.py           # In-memory conversation state per sender
│       ├── message_handler.py              # Routes incoming messages
│       ├── verification.py                 # Meta webhook handshake
│       ├── webhook_handler.py              # Parses webhook payload
│       └── handlers/
│           ├── student_handler.py          # Handles OCR → preview → missing fields
│           ├── confirmation_handler.py     # Handles yes / no / edit
│           └── details_handler.py          # Handles "show details"
├── tests/
│   ├── unit/                               # Mirrors source folder structure
│   │   ├── ai/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── whatsapp/
│   │       └── handlers/
│   ├── integration/
│   │   └── test_student_repository.py      # StudentRepository + Frappe integration tests
│   └── e2e/
│       ├── test_student_e2e.py             # OCR → OpenAI → Frappe e2e test
│       └── test_whatsapp_e2e.py            # WhatsApp → OpenAI → Frappe e2e test
├── static/
│   └── index.html                          # Landing page
├── server.py                               # HTTP server
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
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=your-verify-token
```

## Running the Server

```bash
PORT=8080 python server.py
```

## API

### `POST /feed`
Extracts student data from OCR text using OpenAI and returns a preview for confirmation.

**Request:**
```json
{
  "ocr_text": "John Doe, born 15 August 2005, father Robert Doe, address 123 Main St Mumbai, program Class VIII, academic year 2025-2026"
}
```

**curl:**
```bash
curl -X POST http://localhost:8080/feed \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "John Doe, born 15 August 2005, father Robert Doe, address 123 Main St Mumbai, program Class VIII, academic year 2025-2026"}'
```

**Response (280 — pending confirmation):**
```json
{
  "status": "pending_confirmation",
  "extracted_data": {
    "student_name": "John Doe",
    "date_of_birth": "15/08/2005",
    "address": "123 Main St Mumbai",
    "guardian_name": "Robert Doe",
    "program": "Class VIII",
    "academic_year": "2025-2026"
  },
  "preview": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "2005-08-15",
    "address_line_1": "123 Main St Mumbai"
  }
}
```

## Adding a New Student Field

All field metadata lives in **one place** — `app/models/student.py → STUDENT_FIELDS`.
Adding a single entry automatically propagates to:
- Mandatory validation
- AI system prompt
- Missing field messages (with hint)
- "Show details" display
- Confirmation preview

```python
StudentFieldMeta(
    key="phone_number",
    label="Phone Number",
    prompt_hint="phone_number (student or guardian contact number)",
    mandatory=True,
    model_field="phone_number",
    hint="e.g. +91 9876543210"
)
```

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run by suite:
```bash
# Unit tests (no API calls, instant)
python -m pytest tests/unit/ -v

# Integration tests (real OpenAI + Frappe)
python -m pytest tests/integration/ -v

# End-to-end tests (full pipeline)
python -m pytest tests/e2e/ -v
```

## WhatsApp Chatbot

### Setup

1. Create a [Meta Developer App](https://developers.facebook.com/) and add the WhatsApp product
2. Get your **WhatsApp Token**, **Phone Number ID** and set a **Verify Token**
3. Add the env vars listed above to `.env`
4. Expose your local server:
```bash
ngrok http 8080
```
5. Set webhook URL in Meta Developer Console:
```
https://<ngrok-id>.ngrok.io/webhook
```

### Conversation Flow

```
User:  John Doe, born 15 Aug 2005, father Robert Doe,
       address 123 Main St, program Class VIII, academic year 2025-2026

Bot:   📋 Please verify the student details before saving:
       Name: John Doe
       Date of Birth: 2005-08-15
       Address: 123 Main St
       Guardian: Robert Doe
       Program: Class VIII (2025-2026)
       Reply yes to confirm, no to cancel, or edit to make changes.

User:  edit
Bot:   ✏️ Sure! Send the fields you'd like to change.
       Type "show details" to see what's been entered so far.

User:  academic year 2026-2027
Bot:   📋 Please verify ... [updated preview]

User:  yes
Bot:   ✅ Student created successfully!
       Name: John Doe
       ID: EDU-STU-2026-00001
```

### Commands (work at any point)

| Message | Action |
|---|---|
| `hello` / `hi` | Show welcome & example |
| `show details` / `my details` | Show all fields entered so far |
| `yes` / `confirm` / `ok` | Confirm and create record |
| `no` / `cancel` | Cancel and clear |
| `edit` / `change` / `correct` | Go back to editing without losing data |

### Missing Fields

If any mandatory fields are missing, the bot tells you exactly what's needed with hints:
```
⚠️ Some details are missing. Please provide the following:
• Address
• Program (e.g. Class VIII, Class X)
• Academic Year (e.g. 2025-2026)

You don't need to repeat what you already sent — just provide the missing details.
```

### Duplicate Detection

The bot checks for duplicates (same name + guardian) as soon as both are known — even before all fields are collected. If a duplicate is found, data is preserved so you can correct just the conflicting fields.

### Webhook Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/webhook` | Meta verification handshake |
| `POST` | `/webhook` | Receives WhatsApp messages |

## Deployment

Deployed on [DigitalOcean App Platform](https://cloud.digitalocean.com/apps). Auto-deploys on push to `main`.

Set the following environment variables in DigitalOcean App Settings:
- `OPENAI_API_KEY`
- `FRAPPE_URL`
- `FRAPPE_API_KEY`
- `FRAPPE_API_SECRET`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_VERIFY_TOKEN`

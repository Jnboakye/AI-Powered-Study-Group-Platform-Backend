## StudyDrop Backend

AI-powered backend for **StudyDrop**, a full study platform where students can upload any PDF and instantly get:

- **Auto-generated quiz**: multiple-choice questions that test real understanding  
- **Anki-style flashcards**: front/back cards for spaced repetition  
- **Visual mind map**: hierarchical nodes of concepts and sub-topics  
- **Clean summary**: a concise, student-friendly explanation of the document  
- **AI tutor chat**: a streaming tutor that only answers from the uploaded document

> Live API docs: `https://studydrop-backend.up.railway.app/docs`

---

## Tech stack

- **Backend**: FastAPI  
- **AI provider**: OpenAI (`gpt-4o`)  
- **Runtime**: Uvicorn  
- **PDF processing**: `pdfplumber`, `pdfminer.six`  
- **Deployment**: Railway

---

## Core features

- **PDF upload**
  - Upload a PDF and extract its text.
  - Returns a `doc_id` used by all other endpoints.

- **Quiz generation**
  - Generates multiple-choice questions (with options, correct answer, and explanation).
  - Backed by OpenAI with a strict JSON schema.

- **Anki-style flashcards**
  - Generates concise front/back flashcards focused on key concepts and definitions.

- **Mind map**
  - Builds a 3-level hierarchical mind map (root topic → branches → sub-topics).

- **Summary**
  - Produces a 3–5 paragraph plain-text summary of the document.

- **AI tutor (chat + streaming)**
  - Tutor answers **only** based on the uploaded document content.
  - Supports both standard responses and Server-Sent Events (SSE) streaming.

- **All-in-one generation**
  - Single endpoint that runs quiz, flashcards, mind map, and summary in one call.

---

## Project structure

```text
app/
  main.py            # FastAPI app + router registration
  models.py          # Pydantic models for requests/responses
  routers/
    upload.py        # PDF upload + in-memory document store
    generate.py      # quiz, flashcards, mind map, summary, all-in-one
    tutor.py         # tutor chat + streaming SSE endpoint
  services/
    pdf_service.py   # PDF text extraction + truncation
    claude_service.py# OpenAI integration & prompt engineering
requirements.txt     # Python dependencies
.env.example         # Example environment configuration
Procfile             # Process definition for Railway
railway.toml         # Railway configuration
```

---

## Getting started (local development)

### 1. Prerequisites

- **Python**: 3.10+  
- **OpenAI API key**

### 2. Clone and install

```bash
git clone <your-repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the project root (or copy `.env.example`):

```bash
cp .env.example .env
```

Update `.env` with your OpenAI key:

```text
OPENAI_API_KEY=sk-...
```

### 4. Run the API locally

```bash
uvicorn app.main:app --reload
```

Then open:

- **Swagger UI**: `http://localhost:8000/docs`  
- **Health check**: `http://localhost:8000/` → `{"status": "StudyDrop API is running 🚀"}`

---

## API overview

### Upload

- **POST** `/api/upload/pdf`  
  - **Body**: `multipart/form-data` with `file` (PDF).  
  - **Returns**: `doc_id`, `filename`, `char_count`, and a `preview` of the text.

All other endpoints require a valid `doc_id` from this step.

### Generate

- **POST** `/api/generate/quiz/{doc_id}`  
  - Optional query: `num_questions` (default 8).

- **POST** `/api/generate/flashcards/{doc_id}`  
  - Optional query: `num_cards` (default 15).

- **POST** `/api/generate/mindmap/{doc_id}`

- **POST** `/api/generate/summary/{doc_id}`

- **POST** `/api/generate/all/{doc_id}`  
  - Convenience endpoint that returns quiz, flashcards, mind map, and summary in a single response (slower because it makes multiple AI calls).

### Tutor

- **POST** `/api/tutor/chat`  
  - **Body**: JSON `TutorRequest` with `doc_id` and `messages` (chat history).  
  - **Returns**: `TutorResponse` with a single `reply` string.

- **POST** `/api/tutor/chat/stream`  
  - **Body**: same as `/chat`.  
  - **Returns**: `text/event-stream` (SSE) where each chunk is `data: <token>\n\n`.

For detailed schemas and example payloads, see the live Swagger docs at `https://studydrop-backend.up.railway.app/docs`.

---

## Deployment (Railway)

This backend is configured to run on **Railway**:

- **Procfile** defines the web process:

```text
web: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Railway automatically injects the `PORT` environment variable.  
- You **must** set `OPENAI_API_KEY` as a Railway environment variable.

Once deployed, your API docs are available at:

- `https://studydrop-backend.up.railway.app/docs`

---

## Notes

- The document store is **in-memory** and resets whenever the server restarts.  
- Very large PDFs are truncated to ~40,000 characters before being sent to the AI to keep responses fast and reliable.

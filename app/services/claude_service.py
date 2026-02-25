from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Initialize OpenAI client once — reused across all requests
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"


def _call_ai(system_prompt: str, user_prompt: str) -> str:
    """
    Base helper: calls OpenAI and returns the raw text response.
    All other functions build on this.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
    )
    return response.choices[0].message.content


def _parse_json_response(raw: str) -> any:
    """
    GPT sometimes wraps JSON in markdown code fences like ```json ... ```
    This strips them out so we can parse safely.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]  # Remove first line (```json)
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]  # Remove closing ```
    return json.loads(cleaned.strip())


# ─────────────────────────────────────────────
# QUIZ GENERATION
# ─────────────────────────────────────────────

QUIZ_SYSTEM_PROMPT = """
You are an expert educator who creates high-quality multiple choice quiz questions.
You MUST respond with ONLY valid JSON — no explanation, no markdown, no preamble.
The JSON must match this exact structure:
{
  "questions": [
    {
      "id": 1,
      "question": "...",
      "options": [
        {"label": "A", "text": "..."},
        {"label": "B", "text": "..."},
        {"label": "C", "text": "..."},
        {"label": "D", "text": "..."}
      ],
      "correct_label": "A",
      "explanation": "Brief explanation of why this answer is correct."
    }
  ]
}
"""

def generate_quiz(text: str, num_questions: int = 8) -> dict:
    user_prompt = f"""
Based on the following document, generate exactly {num_questions} multiple choice questions.
Questions should test genuine understanding, not just memorization.
Vary difficulty from easy to challenging.

DOCUMENT:
{text}
"""
    raw = _call_ai(QUIZ_SYSTEM_PROMPT, user_prompt)
    return _parse_json_response(raw)


# ─────────────────────────────────────────────
# FLASHCARD GENERATION
# ─────────────────────────────────────────────

FLASHCARD_SYSTEM_PROMPT = """
You are an expert at creating concise, effective study flashcards using the Anki method.
Front: a clear question or term. Back: a precise, memorable answer.
You MUST respond with ONLY valid JSON — no explanation, no markdown, no preamble.
The JSON must match this exact structure:
{
  "flashcards": [
    {"id": 1, "front": "...", "back": "..."}
  ]
}
"""

def generate_flashcards(text: str, num_cards: int = 15) -> dict:
    user_prompt = f"""
Based on the following document, generate exactly {num_cards} flashcards.
Focus on key concepts, definitions, important facts, and relationships between ideas.

DOCUMENT:
{text}
"""
    raw = _call_ai(FLASHCARD_SYSTEM_PROMPT, user_prompt)
    return _parse_json_response(raw)


# ─────────────────────────────────────────────
# MIND MAP GENERATION
# ─────────────────────────────────────────────

MINDMAP_SYSTEM_PROMPT = """
You are an expert at organizing knowledge into clear hierarchical mind maps.
You MUST respond with ONLY valid JSON — no explanation, no markdown, no preamble.
Rules:
- Exactly ONE node must have parent_id = null (this is the root/central topic)
- All other nodes must reference a valid parent node's id
- Keep labels short (2-5 words max)
- Maximum 3 levels of depth
The JSON must match this exact structure:
{
  "nodes": [
    {"id": "node-1", "label": "Central Topic", "parent_id": null},
    {"id": "node-2", "label": "Main Branch", "parent_id": "node-1"},
    {"id": "node-3", "label": "Sub Topic", "parent_id": "node-2"}
  ]
}
"""

def generate_mindmap(text: str) -> dict:
    user_prompt = f"""
Based on the following document, create a mind map with 12-20 nodes.
Identify the central topic, main branches (key themes), and sub-topics.

DOCUMENT:
{text}
"""
    raw = _call_ai(MINDMAP_SYSTEM_PROMPT, user_prompt)
    return _parse_json_response(raw)


# ─────────────────────────────────────────────
# SUMMARY GENERATION
# ─────────────────────────────────────────────

SUMMARY_SYSTEM_PROMPT = """
You are an expert at summarizing complex documents clearly and concisely.
Write in plain prose — no bullet points. Aim for 3-5 paragraphs.
"""

def generate_summary(text: str) -> str:
    user_prompt = f"""
Write a clear, comprehensive summary of the following document.
Capture the main ideas, key arguments, and important conclusions.
Write for a student who hasn't read the original.

DOCUMENT:
{text}
"""
    return _call_ai(SUMMARY_SYSTEM_PROMPT, user_prompt)


# ─────────────────────────────────────────────
# AI TUTOR CHAT
# ─────────────────────────────────────────────

def chat_with_tutor(context: str, messages: list) -> str:
    """
    The AI tutor. We inject the full document as system context so the AI
    only answers based on what's in the document — not random internet knowledge.
    """
    system_prompt = f"""
You are an expert tutor helping a student understand the following document.
Answer questions clearly and helpfully, always grounded in the document content.
If the answer isn't in the document, say so honestly rather than guessing.
When relevant, mention which section or concept your answer relates to.

DOCUMENT CONTENT:
{context}
"""
    # Build the messages array in the format OpenAI expects
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────
# STREAMING TUTOR CHAT
# ─────────────────────────────────────────────

def stream_tutor_response(context: str, messages: list):
    """
    Same as chat_with_tutor but streams tokens as they arrive.
    This is a Python generator — it yields one chunk at a time.
    Makes the tutor feel alive instead of waiting 5 seconds for a full response.
    """
    system_prompt = f"""
You are an expert tutor helping a student understand the following document.
Answer questions clearly and helpfully, always grounded in the document content.
If the answer isn't in the document, say so honestly rather than guessing.

DOCUMENT CONTENT:
{context}
"""
    api_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    stream = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
        max_tokens=1024,
        stream=True,  # This is the key difference
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
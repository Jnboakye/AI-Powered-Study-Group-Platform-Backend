from pydantic import BaseModel, Field
from typing import Optional, List

# upload 
class UploadResponse (BaseModel):
    doc_id: str
    filename: str
    char_count: int
    preview: str


# Quiz
class QuizOption (BaseModel):
    label: str        # "A", "B", "C", "D"
    text: str

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[QuizOption]
    correct_label: str
    explanation: str

class QuizResponse(BaseModel):
    doc_id: str
    questions: List[QuizQuestion]


#  Flashcards 
class Flashcard(BaseModel):
    id: int
    front: str
    back: str

class FlashcardsResponse(BaseModel):
    doc_id: str
    flashcards: List[Flashcard]


# --- Mind Map ---
class MindMapNode(BaseModel):
    id: str
    label: str
    parent_id: Optional[str] = None

class MindMapResponse(BaseModel):
    doc_id: str
    nodes: List[MindMapNode]


# --- Summary ---
class SummaryResponse(BaseModel):
    doc_id: str
    summary: str


# --- AI Tutor ---
class TutorMessage(BaseModel):
    role: str         # "user" or "assistant"
    content: str

class TutorRequest(BaseModel):
    doc_id: str
    messages: List[TutorMessage]
    context: str

class TutorResponse(BaseModel):
    reply: str
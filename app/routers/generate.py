from fastapi import APIRouter, HTTPException
from app.routers.upload import get_document_text
from app.services import claude_service
from app.models import (
    QuizResponse,
    FlashcardsResponse,
    MindMapResponse,
    SummaryResponse
)
import json

router = APIRouter()


@router.post("/quiz/{doc_id}", response_model=QuizResponse)
async def generate_quiz(doc_id: str, num_questions: int = 8):
    """
    Generate multiple choice quiz questions from an uploaded document.
    doc_id comes from the upload step.
    num_questions defaults to 8 but frontend can change it.
    """
    text = get_document_text(doc_id)

    try:
        result = claude_service.generate_quiz(text, num_questions)
        return QuizResponse(doc_id=doc_id, questions=result["questions"])
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcards/{doc_id}", response_model=FlashcardsResponse)
async def generate_flashcards(doc_id: str, num_cards: int = 15):
    """
    Generate Anki-style flashcards from an uploaded document.
    """
    text = get_document_text(doc_id)

    try:
        result = claude_service.generate_flashcards(text, num_cards)
        return FlashcardsResponse(doc_id=doc_id, flashcards=result["flashcards"])
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mindmap/{doc_id}", response_model=MindMapResponse)
async def generate_mindmap(doc_id: str):
    """
    Generate a hierarchical mind map from an uploaded document.
    """
    text = get_document_text(doc_id)

    try:
        result = claude_service.generate_mindmap(text)
        return MindMapResponse(doc_id=doc_id, nodes=result["nodes"])
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary/{doc_id}", response_model=SummaryResponse)
async def generate_summary(doc_id: str):
    """
    Generate a concise plain text summary of an uploaded document.
    """
    text = get_document_text(doc_id)

    try:
        summary = claude_service.generate_summary(text)
        return SummaryResponse(doc_id=doc_id, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all/{doc_id}")
async def generate_all(doc_id: str):
    """
    Convenience endpoint — generates everything in one call.
    The frontend calls this once after upload instead of 4 separate requests.
    Takes ~20-30 seconds since it makes 4 AI calls sequentially.
    """
    text = get_document_text(doc_id)

    try:
        quiz_result = claude_service.generate_quiz(text)
        flashcard_result = claude_service.generate_flashcards(text)
        mindmap_result = claude_service.generate_mindmap(text)
        summary = claude_service.generate_summary(text)

        return {
            "doc_id": doc_id,
            "quiz": {"questions": quiz_result["questions"]},
            "flashcards": {"flashcards": flashcard_result["flashcards"]},
            "mindmap": {"nodes": mindmap_result["nodes"]},
            "summary": {"summary": summary},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extract_text_from_pdf
from app.models import UploadResponse

router = APIRouter()

# This is our in-memory document store
# Think of it as a temporary dictionary that holds extracted text
# Key = doc_id, Value = extracted text
# ⚠️ This resets every time you restart the server — perfect for MVP
document_store: dict[str, str] = {}


@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload.
    Extracts the text, stores it in memory, and returns a doc_id.
    That doc_id is used in all future requests (quiz, flashcards, etc.)
    """

    # Make sure they actually uploaded a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:
        result = extract_text_from_pdf(file)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Store the extracted text so other endpoints can access it later
    document_store[result["doc_id"]] = result["text"]

    return UploadResponse(
        doc_id=result["doc_id"],
        filename=result["filename"],
        char_count=result["char_count"],
        preview=result["preview"],
    )


def get_document_text(doc_id: str) -> str:
    """
    Helper function used by generate.py and tutor.py
    to retrieve the stored text for a given doc_id.
    """
    text = document_store.get(doc_id)
    if not text:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found. Please upload your PDF first."
        )
    return text
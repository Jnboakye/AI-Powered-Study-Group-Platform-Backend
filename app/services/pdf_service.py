import pdfplumber
import uuid
import tempfile
import os
from fastapi import UploadFile


def extract_text_from_pdf(file: UploadFile) -> dict:
    """
    Takes an uploaded PDF file and extracts all the text from it.
    Returns a dict with a unique doc_id, filename, the full text, and a short preview.
    """

    # Generate a unique ID for this document — used in all future API calls
    doc_id = str(uuid.uuid4())

    # We need to save the file temporarily on disk so pdfplumber can open it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = file.file.read()
        tmp.write(content)
        tmp_path = tmp.name  # e.g. /tmp/abc123.pdf

    try:
        full_text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n"
    finally:
        # Always delete the temp file even if something crashes
        os.unlink(tmp_path)

    # If we got nothing, the PDF is probably image-based (scanned)
    if not full_text.strip():
        raise ValueError("Could not extract text from this PDF. It may be a scanned image.")

    # Truncate to 40,000 chars so we don't overwhelm the AI with huge documents
    MAX_CHARS = 40_000
    truncated_text = full_text[:MAX_CHARS]
    if len(full_text) > MAX_CHARS:
        truncated_text += "\n\n[Document truncated for processing]"

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "text": truncated_text,
        "char_count": len(truncated_text),
        "preview": truncated_text[:300].strip(),
    }
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.routers.upload import get_document_text
from app.services import claude_service
from app.models import TutorRequest, TutorResponse

router = APIRouter()


@router.post("/chat", response_model=TutorResponse)
async def chat(request: TutorRequest):
    """
    Standard tutor chat — waits for the full response then returns it.
    Good as a fallback if streaming doesn't work on the frontend.
    """
    text = get_document_text(request.doc_id)

    try:
        reply = claude_service.chat_with_tutor(
            context=text,
            messages=[m.dict() for m in request.messages],
        )
        return TutorResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: TutorRequest):
    """
    Streaming tutor chat — sends tokens as they arrive from the AI.
    This is what makes the tutor feel like it's typing in real time.
    The frontend reads this as a Server-Sent Events (SSE) stream.
    """
    text = get_document_text(request.doc_id)

    def token_generator():
        try:
            for token in claude_service.stream_tutor_response(
                context=text,
                messages=[m.dict() for m in request.messages],
            ):
                # SSE format — each chunk must look like "data: hello\n\n"
                yield f"data: {token}\n\n"
            # Tell the frontend the stream is finished
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Prevents Nginx from buffering the stream
        },
    )
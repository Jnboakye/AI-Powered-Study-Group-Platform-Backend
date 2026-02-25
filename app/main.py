from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, generate, tutor

app = FastAPI(
    title="StudyDrop API",
    description="AI-powered study material generator",
    version="1.0.0",
)

# CORS — this allows your frontend (Next.js) to talk to this backend
# Without this, the browser would block all requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://web-production-2308c.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers with their URL prefixes
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(tutor.router, prefix="/api/tutor", tags=["Tutor"])


@app.get("/")
def root():
    return {"status": "StudyDrop API is running 🚀"}
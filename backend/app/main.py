from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db.models import create_tables
from backend.app.api.routes.tickets import router as tickets_router
from backend.app.api.routes.knowledge_base import router as knowledge_base_router


app = FastAPI(
    title="AI-Powered Customer Support Ticket Classifier"
)


# Allow frontend (Live Server) to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
create_tables()


# Register ticket API routes
app.include_router(tickets_router)
app.include_router(knowledge_base_router)


@app.get("/")
def home():
    return {
        "message": "Customer Support Ticket Classifier API is running"
    }
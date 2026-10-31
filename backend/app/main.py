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
    allow_origins=["*"],
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
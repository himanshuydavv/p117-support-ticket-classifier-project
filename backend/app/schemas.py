from pydantic import BaseModel, model_validator
from typing import Optional


class TicketCreate(BaseModel):
    subject: str
    body: str
    channel: Optional[str] = "web"
    customer_tier: Optional[str] = "standard"


class TicketCorrection(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None

    @model_validator(mode="after")
    def require_category_or_priority(self):
        if self.category is None and self.priority is None:
            raise ValueError("Provide a category, a priority, or both.")
        return self


class TicketResponse(BaseModel):
    id: int
    subject: str
    body: str
    channel: Optional[str]
    customer_tier: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    sentiment: Optional[str]
    confidence: Optional[float]
    source: Optional[str]
    escalated: bool
    sla: Optional[dict] = None
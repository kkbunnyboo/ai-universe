from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from src.database.db import get_db
from src.models.database import Agent, Conversation, Message

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.status == "active").count()
    total_conversations = db.query(Conversation).count()
    total_messages = db.query(Message).count()
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_conversations": total_conversations,
        "total_messages": total_messages
    }
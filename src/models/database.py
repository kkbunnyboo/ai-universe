from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.db import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    personality = Column(Text)
    model = Column(String(50), default="gpt-4")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())

    conversations = relationship("Conversation", back_populates="agent")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    created_at = Column(DateTime, server_default=func.now())

    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


class FavoriteJoke(Base):
    __tablename__ = "favorite_jokes"

    id = Column(Integer, primary_key=True, index=True)
    joke_id = Column(String(50), nullable=False, index=True)
    category = Column(String(50))
    setup = Column(Text)
    delivery = Column(Text)
    joke_text = Column(Text)
    is_two_part = Column(Boolean, default=False)
    saved_at = Column(DateTime, server_default=func.now())

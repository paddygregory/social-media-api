import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy import JSON, Column, String, Boolean, Integer
import psycopg2
from pydantic import BaseModel


class Post(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str
    tone: str
    length: str
    platform_outputs: Optional[Dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    tokens_used: Optional[int] = None
    user_id: Optional[int] = None

class Job(SQLModel,  table=True):
    __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    status: str
    result: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    email: str
    password: Optional[str]
    google_id: Optional[str] = Field(default=None, sa_column=Column(String))
    auth_provider: str = Field(default="local", sa_column=Column(String))
    tier: str = Field(default="free", sa_column=Column(String))
    stripe_customer_id: Optional[str] = Field(default=None, sa_column=Column(String))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    feedback: str

class FeedbackInput(BaseModel):
    name: str
    email: str
    feedback: str

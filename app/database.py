from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv
import psycopg2
from app.models import Post, Job

load_dotenv()

engine = create_engine(os.getenv("SQL_KEY"), echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine) 
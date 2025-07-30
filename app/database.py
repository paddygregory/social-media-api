from sqlmodel import create_engine, Session, SQLModel, text
import os
from dotenv import load_dotenv
import psycopg2
from app.models import Post, Job, Feedback, User

load_dotenv()

engine = create_engine(os.getenv("SQL_KEY"), echo=True)

def create_db_and_tables():
    
    try:
        with engine.connect() as connection:
            
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'stripe_customer_id'
            """))
            
            if not result.fetchone():
                print("🔧 Adding stripe_customer_id column to user table...")
                connection.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN stripe_customer_id VARCHAR NULL;
                """))
                connection.commit()
                print(" Successfully added stripe_customer_id column")
            
    except Exception as e:
        print(f"Migration attempt: {e}")
        
        pass
    
   
    SQLModel.metadata.create_all(engine)

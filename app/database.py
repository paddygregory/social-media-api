from sqlmodel import create_engine, Session, SQLModel, text, select
import os
from dotenv import load_dotenv
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
                connection.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN stripe_customer_id VARCHAR NULL;
                """))
                connection.commit()
            
    except Exception as e:
        pass
    
   
    SQLModel.metadata.create_all(engine)

async def get_or_create_user(user_info: dict):
    with Session(engine) as session:
        user = session.exec(select(User).where(
            (User.email == user_info.get('email')) |
            (User.google_id == user_info['sub'])
        )
        ).first()

        if user:
            if not user.google_id:
                user.google_id = user_info['sub']
                user.auth_provider = 'google'
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        
        user = User(
            email=user_info.get('email'),
            name=user_info.get('name', 'User'),
            google_id=user_info['sub'],
            auth_provider='google',
            tier='free'
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user 

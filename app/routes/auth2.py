
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from app.models import User
from app.database import engine
from app.auth import hash_password, verify_password, create_access_token, get_current_user

auth_router = APIRouter()

class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

@auth_router.post("/register")
def register(data: RegisterInput):
    with Session(engine) as session:
        user_exists = session.exec(select(User).where(User.email == data.email)).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            tier="free"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}

class LoginInput(BaseModel):
    email: str
    password: str

@auth_router.post("/login")
def login(data: LoginInput):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "tier": user.tier,
        "created_at": user.created_at
    }

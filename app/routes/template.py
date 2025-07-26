from fastapi import APIRouter

template_router = APIRouter()

@template_router.get("/templates")
def get_templates():
    return {"tones": ["professional", "witty", "casual"], "lengths": ["short", "medium", "long"]}
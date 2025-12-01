from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gemini_service import GeminiService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    model_type: str = "fast"

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        service = GeminiService()
        response_text = service.generate_content(request.message, model_type=request.model_type)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

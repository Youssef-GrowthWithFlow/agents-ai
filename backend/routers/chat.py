from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from services.chat_service import ChatService
from db.database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model_type: str = "fast"
    use_rag: bool = False

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    metadata: dict

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: list

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Chat endpoint with conversation history support.

    - Creates new conversation if conversation_id is not provided
    - Maintains conversation context across messages
    - Optional RAG mode using knowledge base
    """
    try:
        chat_service = ChatService(db)

        # Convert conversation_id to UUID if provided
        conversation_id = UUID(request.conversation_id) if request.conversation_id else None

        result = await chat_service.chat(
            conversation_id=conversation_id,
            user_message=request.message,
            model_type=request.model_type,
            use_rag=request.use_rag
        )

        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/new")
async def create_conversation(db: AsyncSession = Depends(get_db)):
    """Creates a new conversation session."""
    try:
        chat_service = ChatService(db)
        conversation_id = await chat_service.create_conversation()
        return {"conversation_id": str(conversation_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves conversation history."""
    try:
        chat_service = ChatService(db)
        messages = await chat_service.get_conversation_history(UUID(conversation_id))
        return {
            "conversation_id": conversation_id,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

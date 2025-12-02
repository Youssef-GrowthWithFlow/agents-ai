from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from services.knowledge_base_service import KnowledgeBaseService
from db.database import get_db

router = APIRouter(
    prefix="/knowledge-base",
    tags=["knowledge-base"]
)

class QueryRequest(BaseModel):
    query: str
    model_type: str = "fast"

@router.post("/sync")
async def sync_knowledge_base(db: AsyncSession = Depends(get_db)):
    """
    Synchronously syncs the knowledge base from Notion to PostgreSQL.
    This is a heavy operation.
    """
    try:
        kb_service = KnowledgeBaseService(db)
        result = await kb_service.sync_knowledge_base()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_knowledge_base(request: QueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Queries the knowledge base using RAG.
    """
    try:
        kb_service = KnowledgeBaseService(db)
        result = await kb_service.query_with_rag(request.query, request.model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

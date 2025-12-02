from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Conversation, Message
from services.gemini_service import GeminiService
from services.knowledge_base_service import KnowledgeBaseService
from uuid import UUID

class ChatService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.gemini_service = GeminiService()
        self.kb_service = KnowledgeBaseService(db_session)

    async def create_conversation(self, metadata: dict = None) -> UUID:
        """Creates a new conversation session."""
        conversation = Conversation(meta=metadata or {})
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation.id

    async def get_conversation_history(self, conversation_id: UUID, limit: int = 50) -> List[dict]:
        """Retrieves conversation history."""
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(limit)

        result = await self.db.execute(stmt)
        messages = result.scalars().all()

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "metadata": msg.meta
            }
            for msg in messages
        ]

    async def add_message(self, conversation_id: UUID, role: str, content: str, metadata: dict = None):
        """Adds a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            meta=metadata or {}
        )
        self.db.add(message)
        await self.db.commit()

    async def chat(
        self,
        conversation_id: Optional[UUID],
        user_message: str,
        model_type: str = "fast",
        use_rag: bool = False
    ) -> dict:
        """
        Main chat endpoint with conversation history.

        Args:
            conversation_id: Existing conversation ID or None to create new
            user_message: User's message
            model_type: Gemini model type ("fast" or "intelligent")
            use_rag: Whether to use RAG with knowledge base
        """
        # Create new conversation if needed
        if not conversation_id:
            conversation_id = await self.create_conversation()

        # Store user message
        await self.add_message(conversation_id, "user", user_message)

        # Get conversation history for context
        history = await self.get_conversation_history(conversation_id, limit=10)

        # Build prompt with history
        if use_rag:
            # RAG mode: Use knowledge base
            rag_result = await self.kb_service.query_with_rag(user_message, model_type)
            assistant_response = rag_result["answer"]
            metadata = {
                "sources": rag_result["sources"],
                "model_type": model_type,
                "rag_enabled": True
            }
        else:
            # Regular chat mode with history
            prompt = self._build_prompt_with_history(history, user_message)
            assistant_response = self.gemini_service.generate_content(prompt, model_type)
            metadata = {
                "model_type": model_type,
                "rag_enabled": False
            }

        # Store assistant response
        await self.add_message(conversation_id, "assistant", assistant_response, metadata)

        return {
            "conversation_id": str(conversation_id),
            "response": assistant_response,
            "metadata": metadata
        }

    def _build_prompt_with_history(self, history: List[dict], current_message: str) -> str:
        """Builds a prompt including conversation history."""
        prompt_parts = ["You are a helpful assistant for the 'Growth with Flow' project.\n\nConversation history:"]

        for msg in history[:-1]:  # Exclude the current message we just added
            role_label = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role_label}: {msg['content']}")

        prompt_parts.append(f"\nUser: {current_message}\n\nAssistant:")

        return "\n".join(prompt_parts)

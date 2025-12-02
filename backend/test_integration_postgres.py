import asyncio
import sys
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from db.database import Base, DATABASE_URL
from db.models import Document, Embedding, Conversation, Message
from services.knowledge_base_service import KnowledgeBaseService
from services.chat_service import ChatService

load_dotenv()

async def test_full_integration():
    """
    Integration test:
    1. Sync real Notion data to PostgreSQL
    2. Verify embeddings are stored
    3. Test RAG query
    4. Test conversation history
    """

    # Create test database session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n=== TEST 1: Sync Knowledge Base ===")
        kb_service = KnowledgeBaseService(session)

        try:
            result = await kb_service.sync_knowledge_base()
            print(f"✓ Sync successful: {result}")

            assert result["status"] == "success"
            assert result["documents_loaded"] > 0
            assert result["chunks_created"] > 0
        except Exception as e:
            print(f"✗ Sync failed: {e}")
            return False

        print("\n=== TEST 2: Verify Data in PostgreSQL ===")
        # Count documents
        doc_count = await session.scalar(select(func.count(Document.id)))
        emb_count = await session.scalar(select(func.count(Embedding.id)))

        print(f"✓ Documents in DB: {doc_count}")
        print(f"✓ Embeddings in DB: {emb_count}")

        assert doc_count > 0, "No documents found in database"
        assert emb_count > 0, "No embeddings found in database"

        print("\n=== TEST 3: Test RAG Query ===")
        query = "What is the company mission?"
        try:
            result = await kb_service.query_with_rag(query, model_type="fast")
            print(f"Query: {query}")
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Sources: {len(result['sources'])} documents used")

            assert result["answer"], "No answer generated"
            assert len(result["sources"]) > 0, "No sources found"
        except Exception as e:
            print(f"✗ RAG query failed: {e}")
            return False

        print("\n=== TEST 4: Test Conversation History ===")
        chat_service = ChatService(session)

        # Create conversation
        conv_id = await chat_service.create_conversation()
        print(f"✓ Created conversation: {conv_id}")

        # Send first message
        response1 = await chat_service.chat(
            conversation_id=conv_id,
            user_message="Hello, how are you?",
            model_type="fast",
            use_rag=False
        )
        print(f"✓ First message response: {response1['response'][:100]}...")

        # Send follow-up message
        response2 = await chat_service.chat(
            conversation_id=conv_id,
            user_message="What did I just ask you?",
            model_type="fast",
            use_rag=False
        )
        print(f"✓ Follow-up response: {response2['response'][:100]}...")

        # Verify history
        history = await chat_service.get_conversation_history(conv_id)
        print(f"✓ Conversation history: {len(history)} messages")

        assert len(history) == 4, f"Expected 4 messages, got {len(history)}"

        print("\n=== TEST 5: Test RAG with Conversation ===")
        response3 = await chat_service.chat(
            conversation_id=conv_id,
            user_message="What is in our knowledge base about the mission?",
            model_type="fast",
            use_rag=True
        )
        print(f"✓ RAG response: {response3['response'][:100]}...")
        print(f"✓ Sources used: {len(response3['metadata'].get('sources', []))}")

        print("\n=== ALL TESTS PASSED ===")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    sys.exit(0 if success else 1)

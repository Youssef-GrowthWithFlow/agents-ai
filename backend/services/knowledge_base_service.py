from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import NotionDBLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from db.models import Document, Embedding
from services.gemini_service import GeminiService
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class KnowledgeBaseService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_KNOWLEDGE_DATABASE_ID")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=self.gemini_api_key
        )

        self.gemini_service = GeminiService()

    async def sync_knowledge_base(self):
        """
        Syncs data from Notion to PostgreSQL with pgvector embeddings.
        Full sync: deletes all existing data and re-indexes.
        """
        if not self.notion_token or not self.database_id:
            raise ValueError("Cannot sync: Notion credentials missing.")

        print("Loading data from Notion...")
        loader = NotionDBLoader(
            integration_token=self.notion_token,
            database_id=self.database_id,
            request_timeout_sec=30,
        )

        # NotionDBLoader.load() is synchronous, run in thread pool
        docs = await asyncio.to_thread(loader.load)
        print(f"Loaded {len(docs)} documents from Notion.")

        if not docs:
            print("No documents found in Notion database.")
            return {"status": "success", "message": "No documents found to sync."}

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        # Clear existing data (full sync approach)
        await self.db.execute(delete(Document))
        await self.db.commit()
        print("Cleared existing knowledge base.")

        total_chunks = 0

        for doc in docs:
            # Extract Notion page metadata
            source_id = doc.metadata.get("id", str(hash(doc.page_content)))
            title = doc.metadata.get("title", "Untitled")

            # Create document record
            db_doc = Document(
                source_id=source_id,
                title=title,
                content=doc.page_content,
                meta=self._filter_metadata(doc.metadata)
            )
            self.db.add(db_doc)
            await self.db.flush()

            # Split into chunks
            chunks = text_splitter.split_text(doc.page_content)

            # Generate embeddings for all chunks (batch operation)
            embeddings_list = await self._generate_embeddings_batch(chunks)

            # Store embeddings
            for idx, (chunk_text, embedding_vector) in enumerate(zip(chunks, embeddings_list)):
                db_embedding = Embedding(
                    document_id=db_doc.id,
                    chunk_text=chunk_text,
                    chunk_index=idx,
                    embedding=embedding_vector,
                    meta={"source_title": title}
                )
                self.db.add(db_embedding)

            total_chunks += len(chunks)
            print(f"Processed document: {title} ({len(chunks)} chunks)")

        await self.db.commit()
        print(f"Knowledge base sync complete. {len(docs)} documents, {total_chunks} chunks indexed.")

        return {
            "status": "success",
            "documents_loaded": len(docs),
            "chunks_created": total_chunks
        }

    async def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch operation)."""
        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings

    def _filter_metadata(self, metadata: dict) -> dict:
        """Filter out complex metadata types that can't be stored in JSONB."""
        filtered = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                filtered[key] = value
            elif isinstance(value, dict):
                filtered[key] = self._filter_metadata(value)
        return filtered

    async def get_relevant_context(self, query: str, k: int = 4) -> List[dict]:
        """
        Retrieves relevant document chunks using pgvector cosine similarity.
        """
        # Generate embedding for the query
        query_embedding = await self.embeddings.aembed_query(query)

        # Perform vector similarity search using pgvector
        stmt = select(Embedding).order_by(
            Embedding.embedding.cosine_distance(query_embedding)
        ).limit(k)

        result = await self.db.execute(stmt)
        embeddings = result.scalars().all()

        # Format results similar to LangChain Document format
        context_docs = []
        for emb in embeddings:
            context_docs.append({
                "page_content": emb.chunk_text,
                "metadata": {
                    **emb.meta,
                    "document_id": str(emb.document_id),
                    "chunk_index": emb.chunk_index
                }
            })

        return context_docs

    async def query_with_rag(self, query: str, model_type: str = "fast"):
        """
        Queries the Gemini model with context from the knowledge base (RAG).
        """
        # 1. Retrieve context
        docs = await self.get_relevant_context(query)
        context_text = "\n\n".join([doc["page_content"] for doc in docs])

        # 2. Construct Prompt
        prompt = f"""
You are a helpful assistant for the 'Growth with Flow' project.
Use the following pieces of context to answer the user's question.
If you don't know the answer based on the context, say so. Do not make up information.

Context:
{context_text}

Question:
{query}

Answer:
"""

        # 3. Generate Answer using Gemini
        response = self.gemini_service.generate_content(
            prompt=prompt,
            model_type=model_type
        )

        return {
            "answer": response,
            "context_used": [doc["page_content"] for doc in docs],
            "sources": [doc["metadata"] for doc in docs]
        }

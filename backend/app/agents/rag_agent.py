"""
📚 Agricultural RAG Agent
Retrieves relevant context from agricultural knowledge base using pgvector similarity search
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.providers.ai_provider import AIProvider
from app.rag.pipeline import similarity_search

SYSTEM_PROMPT = """You are an agricultural knowledge expert. Using the provided knowledge base context,
answer farming questions accurately and practically. Always cite relevant information from the context.
If the context doesn't contain relevant info, say so and provide general guidance."""


async def run(
    provider: AIProvider,
    query: str,
    db: Session,
    crop: Optional[str] = None,
    farm_context: Optional[str] = None,
) -> dict:
    """Run the Agricultural RAG Agent."""

    # Retrieve relevant context
    search_query = query
    if crop:
        search_query = f"{crop} {query}"

    retrieved_chunks = similarity_search(db, search_query, top_k=4)

    if not retrieved_chunks:
        context_text = "No specific knowledge base entries found. Providing general guidance."
        sources = []
    else:
        context_text = "\n\n".join([f"[{c['source']}]\n{c['text']}" for c in retrieved_chunks])
        sources = list(set([c["source"] for c in retrieved_chunks]))

    prompt = f"""Knowledge Base Context:
{context_text}

{"Farm Context: " + farm_context if farm_context else ""}

Farmer's Question: {query}

Using the knowledge base context above, provide a precise, practical answer.
Reference the specific sources where relevant. Keep response under 200 words."""

    try:
        result = await provider.generate(prompt, SYSTEM_PROMPT)
        return {
            "agent": "Agricultural RAG Agent",
            "success": True,
            "response": result,
            "sources": sources,
            "retrieved_chunks": len(retrieved_chunks),
            "context_used": bool(retrieved_chunks),
        }
    except Exception as e:
        fallback = _fallback_from_chunks(retrieved_chunks, query)
        return {
            "agent": "Agricultural RAG Agent",
            "success": False,
            "response": fallback,
            "sources": sources,
            "retrieved_chunks": len(retrieved_chunks),
            "context_used": bool(retrieved_chunks),
            "error": str(e),
        }


def _fallback_from_chunks(chunks: List[dict], query: str) -> str:
    if not chunks:
        return "Agricultural knowledge base search complete. Please consult your local agricultural extension officer for specific advice."
    top = chunks[0]
    return f"Based on agricultural knowledge ({top['source']}): {top['text'][:300]}..."

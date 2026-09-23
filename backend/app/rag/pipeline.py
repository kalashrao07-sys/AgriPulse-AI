"""
Agricultural RAG Pipeline
Chunks documents → Embeddings → pgvector → Similarity Search → Context
"""
from typing import List, Optional
import re
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.models import KnowledgeDocument, KnowledgeChunk

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    EMBEDDINGS_AVAILABLE = True
except Exception:
    _model = None
    EMBEDDINGS_AVAILABLE = False


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """Split text into overlapping chunks."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = []
    current_len = 0
    for sentence in sentences:
        current.append(sentence)
        current_len += len(sentence)
        if current_len >= chunk_size:
            chunks.append(" ".join(current))
            # overlap: keep last few sentences
            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current):
                overlap_len += len(s)
                overlap_sentences.insert(0, s)
                if overlap_len >= overlap:
                    break
            current = overlap_sentences
            current_len = sum(len(s) for s in current)
    if current:
        chunks.append(" ".join(current))
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using sentence-transformers (384-dim)."""
    if not EMBEDDINGS_AVAILABLE or _model is None:
        return [[0.0] * 384 for _ in texts]
    embeddings = _model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def ingest_document(db: Session, title: str, category: str, content: str) -> KnowledgeDocument:
    """Ingest a document into the RAG knowledge base."""
    # Check if already exists
    existing = db.query(KnowledgeDocument).filter(KnowledgeDocument.title == title).first()
    if existing:
        return existing

    doc = KnowledgeDocument(title=title, category=category, content=content)
    db.add(doc)
    db.flush()

    chunks = chunk_text(content)
    embeddings = embed_texts(chunks)

    for chunk_text_val, embedding in zip(chunks, embeddings):
        chunk = KnowledgeChunk(
            document_id=doc.id,
            chunk_text=chunk_text_val,
            embedding=embedding,
        )
        db.add(chunk)

    db.commit()
    db.refresh(doc)
    return doc


def similarity_search(db: Session, query: str, top_k: int = 4) -> List[dict]:
    """Find most relevant knowledge chunks for a query."""
    if not EMBEDDINGS_AVAILABLE or _model is None:
        # Fallback: keyword search
        return keyword_search(db, query, top_k)

    query_embedding = _model.encode([query], normalize_embeddings=True)[0].tolist()

    try:
        # pgvector cosine distance
        # Embedding is interpolated directly as a literal vector string (float array we own — not user input).
        # Cannot use a bind param here because SQLAlchemy's :name syntax conflicts with Postgres ::cast syntax.
        vec_literal = "[" + ",".join(str(x) for x in query_embedding) + "]"
        results = db.execute(
            text(f"""
            SELECT kc.chunk_text, kd.title, kd.category,
                   1 - (kc.embedding <=> '{vec_literal}'::vector) AS similarity
            FROM knowledge_chunks kc
            JOIN knowledge_documents kd ON kc.document_id = kd.id
            WHERE kc.embedding IS NOT NULL
            ORDER BY kc.embedding <=> '{vec_literal}'::vector
            LIMIT :top_k
            """),
            {"top_k": top_k},
        ).fetchall()

        return [
            {
                "text": r[0],
                "source": r[1],
                "category": r[2],
                "similarity": float(r[3]),
            }
            for r in results
        ]
    except Exception:
        return keyword_search(db, query, top_k)


def keyword_search(db: Session, query: str, top_k: int = 4) -> List[dict]:
    """Simple keyword fallback search."""
    keywords = query.lower().split()
    chunks = db.query(KnowledgeChunk).join(KnowledgeDocument).all()
    scored = []
    for chunk in chunks:
        score = sum(1 for kw in keywords if kw in chunk.chunk_text.lower())
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in scored[:top_k]:
        results.append({
            "text": chunk.chunk_text,
            "source": chunk.document.title,
            "category": chunk.document.category,
            "similarity": score / len(keywords) if keywords else 0,
        })
    return results

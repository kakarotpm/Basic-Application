"""The vector database: stores policy passages and finds the ones closest in meaning to a question.

This is the only file that knows we use Chroma. To switch to pgvector later,
rewrite these two functions and keep their inputs and outputs the same.
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from app.rag.documents import Chunk

STORE_DIR = Path(__file__).resolve().parents[2] / "vector_store"
COLLECTION = "hr_policies"

# The embedding model turns text into a list of 384 numbers that capture its meaning.
# It's a small free model (all-MiniLM-L6-v2) that runs on this computer; it's
# downloaded automatically (~80 MB) the first time it's used.
_embedding_model = DefaultEmbeddingFunction()


def _client():
    return chromadb.PersistentClient(path=str(STORE_DIR), settings=Settings(anonymized_telemetry=False))


def rebuild_index(chunks: list[Chunk]) -> None:
    """Throw away the old index and store these passages instead."""
    client = _client()
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    collection = client.create_collection(
        COLLECTION,
        embedding_function=_embedding_model,
        metadata={"hnsw:space": "cosine"},  # compare passages by "angle" between their meanings
    )
    collection.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=[c.text for c in chunks],
        metadatas=[{"source": c.source, "pages": c.pages} for c in chunks],
    )


def search(question: str, top_k: int = 5) -> list[dict]:
    """The top_k passages closest in meaning to the question, best first.

    Each result: {"text", "source", "pages", "score"}, where score runs from
    0 (unrelated) to 1 (identical meaning).
    """
    try:
        collection = _client().get_collection(COLLECTION, embedding_function=_embedding_model)
    except Exception:
        raise RuntimeError("The policy index hasn't been built yet. Run: python -m app.rag.build_index")

    result = collection.query(query_texts=[question], n_results=top_k)
    return [
        {"text": text, "source": meta["source"], "pages": meta["pages"], "score": round(1 - distance, 3)}
        for text, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
    ]

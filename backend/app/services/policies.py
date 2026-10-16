"""HR policy search, as a plain function.

Used by the /policies/search endpoint, by the chatbot (Stage 2), and later
as a tool for the AI agent (Stage 3).
"""

from app.rag import vector_store


class PolicyIndexMissingError(Exception):
    """The policy PDFs haven't been indexed yet (run: python -m app.rag.build_index)."""


def search_policies(question: str, top_k: int = 5) -> list[dict]:
    """The policy passages closest in meaning to the question, best first.

    Each result: {"text", "source", "pages", "score"} (score 0-1, higher = closer match).
    """
    try:
        return vector_store.search(question, top_k)
    except RuntimeError as error:
        raise PolicyIndexMissingError(str(error))

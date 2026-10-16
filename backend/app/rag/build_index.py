"""Build (or rebuild) the policy search index from the PDFs in backend/policies/.

Run from the backend folder whenever the policy PDFs change:
    .\\.venv\\Scripts\\python.exe -m app.rag.build_index
"""

from collections import Counter

from app.rag.documents import POLICIES_DIR, load_all_chunks
from app.rag.vector_store import rebuild_index


def main() -> None:
    chunks, notes = load_all_chunks()
    if not chunks:
        print(f"No PDFs with text found in {POLICIES_DIR}")
        return

    for note in notes:
        print("Note:", note)

    print("\nEmbedding passages and saving the index (the first run also downloads the model)...")
    rebuild_index(chunks)

    print(f"\nIndexed {len(chunks)} passages:")
    for source, count in sorted(Counter(c.source for c in chunks).items()):
        print(f"  {count:3d}  {source}")


if __name__ == "__main__":
    main()

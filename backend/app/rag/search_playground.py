"""Type a question and see which policy passages the search finds (no AI answer, just retrieval).

Run from the backend folder:
    .\\.venv\\Scripts\\python.exe -m app.rag.search_playground "How many sick leaves do I get?"
Add a number at the end to change how many results are shown (default 3):
    .\\.venv\\Scripts\\python.exe -m app.rag.search_playground "work from home" 5
"""

import sys
import textwrap

from app.rag.vector_store import search


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m app.rag.search_playground "your question" [number of results]')
        return
    question = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    print(f'Question: "{question}"\n')
    for rank, result in enumerate(search(question, top_k), start=1):
        print(f"#{rank}  score {result['score']:.2f}   {result['source']}, page {result['pages']}")
        print(textwrap.indent(result["text"], "    "))
        print()


if __name__ == "__main__":
    main()

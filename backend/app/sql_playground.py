"""Run a SQL query against the app's database and print the results as a table.

Run from the backend folder:
    .\\.venv\\Scripts\\python.exe -m app.sql_playground "SELECT name, department FROM employees"
"""

import sys

from sqlalchemy import text

from app.database import engine


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m app.sql_playground "SELECT ..."')
        return
    query = sys.argv[1]

    with engine.connect() as connection:  # changes are never committed, so the data stays as it is
        result = connection.execute(text(query))
        if not result.returns_rows:
            print("Query ran, but it doesn't return rows (and changes were not saved).")
            return
        columns = list(result.keys())
        rows = [[("" if v is None else str(v)) for v in row] for row in result]

    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(columns)]
    print(" | ".join(c.ljust(w) for c, w in zip(columns, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(v.ljust(w) for v, w in zip(row, widths)))
    print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")


if __name__ == "__main__":
    main()

from pathlib import Path

ROOT = Path(__file__).parent

PATHS = {
    "schema": ROOT / "db" / "sql" / "schema.sql",
    "seed": ROOT / "db" / "sql" / "seed.sql",
    "db": ROOT / "dados.db",
}

print(PATHS)

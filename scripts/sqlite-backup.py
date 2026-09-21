"""Create a consistent SQLite backup without copying a live WAL file directly."""
import argparse
import sqlite3
from pathlib import Path


def database_path(value: str) -> Path:
    prefix = "sqlite:///"
    if not value.startswith(prefix): raise ValueError("only sqlite:/// database URLs are supported")
    return Path(value.removeprefix(prefix)).resolve()


def main():
    parser = argparse.ArgumentParser(description="Backup consistente do SQLite do AgentScope")
    parser.add_argument("source", help="URL sqlite:/// absoluta ou relativa")
    parser.add_argument("output", type=Path, help="Novo arquivo de backup")
    args = parser.parse_args()
    source = database_path(args.source)
    output = args.output.resolve()
    if not source.is_file(): raise SystemExit(f"Banco de origem inexistente: {source}")
    if output.exists(): raise SystemExit(f"Destino já existe e não será sobrescrito: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as origin, sqlite3.connect(output) as destination:
        origin.backup(destination)
    print(output)


if __name__ == "__main__": main()

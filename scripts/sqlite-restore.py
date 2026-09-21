"""Restore a SQLite backup only when the destination is explicitly empty."""
import argparse
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Restaura um backup SQLite do AgentScope")
    parser.add_argument("backup", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    backup, destination = args.backup.resolve(), args.destination.resolve()
    if not backup.is_file(): raise SystemExit(f"Backup inexistente: {backup}")
    if destination.exists(): raise SystemExit(f"Destino já existe e não será sobrescrito: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(backup) as source, sqlite3.connect(destination) as target:
        source.backup(target)
        count = target.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]
    if not count: raise SystemExit("Backup não continha tabelas SQLite")
    print(destination)


if __name__ == "__main__": main()

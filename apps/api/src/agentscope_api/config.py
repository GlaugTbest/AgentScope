from dataclasses import dataclass
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Settings:
    api_key: str
    database_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        key = os.getenv("AGENTSCOPE_API_KEY", "dev")
        if not key:
            raise RuntimeError("AGENTSCOPE_API_KEY must not be empty")
        url = os.getenv("AGENTSCOPE_DATABASE_URL", "sqlite:///./data/agentscope.db")
        if url.startswith("sqlite:///./"):
            url = f"sqlite:///{ROOT / url.removeprefix('sqlite:///./')}"
        return cls(key, url)

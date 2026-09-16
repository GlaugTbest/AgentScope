import secrets
from fastapi import Header, HTTPException
from .config import Settings

def require_key(settings: Settings):
    def dependency(authorization: str | None = Header(default=None)):
        expected = f"Bearer {settings.api_key}"
        if not authorization or not secrets.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="unauthorized")
    return dependency

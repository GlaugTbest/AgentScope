"""Shared local-only utilities for the executable AgentScope reference apps."""
import json
import urllib.error
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def ollama(model: str, prompt: str) -> dict:
    """Call only a loopback Ollama server; no hosted model endpoint is used."""
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read())
    except urllib.error.URLError as error:
        raise RuntimeError("Ollama local não está disponível em http://127.0.0.1:11434") from error


def usage(result: dict) -> dict:
    return {"input_tokens": result.get("prompt_eval_count", 0), "output_tokens": result.get("eval_count", 0), "estimated_cost": "0"}

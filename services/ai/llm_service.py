import os
import json
import re
import time
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "300"))
REQUEST_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", os.getenv("LLM_TIMEOUT", "60")))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")

DEFAULT_SYSTEM_MSG = (
    "You are MediKiosk's clinical documentation assistant. "
    "Do not diagnose or prescribe. Return only valid JSON when "
    "JSON is requested. Preserve patient facts exactly."
)


def _clean_json_text(text: str) -> str:
    """Strip markdown formatting and isolate valid JSON content."""
    if not text:
        return ""
    t = text.strip()

    # Strip code block fences e.g. ```json ... ``` or ``` ... ```
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1:]
        else:
            t = t.lstrip("`")
        if t.endswith("```"):
            t = t[:-3]
        t = t.strip()

    # Direct validation
    try:
        json.loads(t)
        return t
    except Exception:
        pass

    # Fallback regex extraction of first { ... } or [ ... ] block
    m = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', t)
    if m:
        candidate = m.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    return t


def _call_ollama(prompt, max_tokens=None, temperature=0.1, system_msg=None, format_json=False):
    """
    Call the local Ollama API running Gemma 4 (gemma4:e4b).
    Returns (content, "OLLAMA_GEMMA4") or None on failure.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL).rstrip("/")
    model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
    timeout = int(os.getenv("OLLAMA_TIMEOUT", REQUEST_TIMEOUT))

    sys_text = system_msg or DEFAULT_SYSTEM_MSG
    url = f"{base_url}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_text},
            {"role": "user", "content": prompt},
        ],
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens or MAX_TOKENS,
        },
        "think": False,
        "stream": False,
    }

    if format_json:
        payload["format"] = "json"

    try:
        r = requests.post(
            url,
            json=payload,
            timeout=timeout,
        )
        r.raise_for_status()
        body = r.json()

        message = body.get("message", {})
        content = message.get("content", "").strip()

        if not content:
            logger.warning("Ollama (%s) returned empty content", model)
            return None

        if format_json:
            cleaned = _clean_json_text(content)
            try:
                json.loads(cleaned)
                logger.info("LLM response via OLLAMA_GEMMA4 (JSON)")
                return cleaned, "OLLAMA_GEMMA4"
            except Exception as pe:
                logger.warning("Ollama (%s) returned invalid JSON: %s | Content: %s", model, pe, content[:200])
                return None

        logger.info("LLM response via OLLAMA_GEMMA4")
        return content, "OLLAMA_GEMMA4"

    except requests.exceptions.ConnectionError:
        logger.warning("Ollama connection error at %s. Ensure `ollama serve` is running.", base_url)
        return None
    except requests.exceptions.Timeout:
        logger.warning("Ollama request timed out after %ss for model %s", timeout, model)
        return None
    except Exception as e:
        logger.warning("Ollama API call failed: %s", e)
        return None


# ── Public API ──────────────────────────────────────────────────────

def generate_json(prompt, fallback, max_tokens=None):
    """
    Generate JSON from the LLM.
    Primary: Local Ollama Gemma 4 (gemma4:e4b).
    Fallback: Local rules.
    """
    result = _call_ollama(prompt, max_tokens=max_tokens, temperature=0.1, format_json=True)
    if result:
        return result

    logger.info("Local Ollama LLM unavailable, using LOCAL_RULES fallback")
    return fallback, "LOCAL_RULES"


def generate_text(prompt, max_tokens=None, temperature=0.1):
    """
    Generate free-form text from the LLM.
    Primary: Local Ollama Gemma 4 (gemma4:e4b).
    Fallback: Local rules.
    """
    result = _call_ollama(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        system_msg=(
            "You are MediKiosk's clinical documentation assistant. "
            "Do not diagnose or prescribe."
        ),
        format_json=False,
    )
    if result:
        return result

    logger.info("Local Ollama LLM unavailable, using LOCAL_RULES fallback")
    return "[LOCAL_FALLBACK]", "LOCAL_RULES"

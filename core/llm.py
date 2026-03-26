import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_MODEL_NAME = "gemini-2.0-flash-lite"
_MAX_RETRIES = 3

_REQUIRED_FIELDS = {"file", "class", "method", "principle", "reasoning", "confidence"}

_JSON_SCHEMA = """\
Respond ONLY with a single valid JSON object — no markdown, no extra text — matching this schema exactly:
{
  "file": "<file path string>",
  "class": "<class name, or 'ModuleLevel' if none>",
  "method": "<method name>",
  "symbol_name": "<class.method>",
  "line_range": "<e.g. L10-L20>",
  "principle": "<one of: SRP, OCP, LSP, ISP, DIP>",
  "reasoning": "<explanation of why this is a violation>",
  "confidence": <float between 0.0 and 1.0>
}"""


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _validate(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if not _REQUIRED_FIELDS.issubset(data.keys()):
        return False
    if not isinstance(data.get("confidence"), (int, float)):
        return False
    return True


def _normalize(data: Dict[str, Any]) -> Dict[str, object]:
    class_name = str(data.get("class", "ModuleLevel"))
    method_name = str(data.get("method", "unknown_method"))
    data.setdefault("symbol_name", f"{class_name}.{method_name}")
    data.setdefault("line_range", "L1-L1")
    data["confidence"] = float(data["confidence"])
    return data


def _extract_retry_seconds(error_message: str) -> float:
    match = re.search(r"retry[_\s]delay[^0-9]*([0-9]+)", str(error_message), re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0


def call_llm(prompt: str) -> Dict[str, object]:
    """Call Gemini API and return a validated SOLID violation analysis as a dict."""
    client = _get_client()
    initial_prompt = f"{prompt}\n\n{_JSON_SCHEMA}"

    last_error = "unknown error"
    for attempt in range(_MAX_RETRIES):
        try:
            if attempt == 0:
                request = initial_prompt
            else:
                request = (
                    f"{initial_prompt}\n\n"
                    f"Your previous response was rejected. Reason: {last_error}\n"
                    f"Correct your output and respond with valid JSON only."
                )

            response = client.models.generate_content(model=_MODEL_NAME, contents=request)
            raw = _strip_fences(response.text)
            data = json.loads(raw)

            if not _validate(data):
                missing = _REQUIRED_FIELDS - set(data.keys()) if isinstance(data, dict) else _REQUIRED_FIELDS
                last_error = f"missing required fields: {missing}"
                continue

            return _normalize(data)

        except json.JSONDecodeError as exc:
            last_error = f"invalid JSON — {exc}"
        except Exception as exc:
            last_error = str(exc)
            retry_secs = _extract_retry_seconds(last_error)
            sleep_secs = retry_secs if retry_secs > 0 else 2 ** attempt
            if attempt < _MAX_RETRIES - 1:
                time.sleep(sleep_secs)

    raise RuntimeError(
        f"Gemini failed to return valid JSON after {_MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_MODEL_NAME = "gemini-2.5-flash"
_MAX_RETRIES = 5

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

_JSON_SCHEMA_BATCH = """\
Respond ONLY with a valid JSON array — no markdown, no extra text — where each element matches this schema:
{
  "file": "<file path string>",
  "class": "<class name, or 'ModuleLevel' if none>",
  "method": "<method name>",
  "symbol_name": "<class.method>",
  "line_range": "<e.g. L10-L20>",
  "principle": "<one of: SRP, OCP, LSP, ISP, DIP>",
  "reasoning": "<explanation of why this is a violation>",
  "confidence": <float between 0.0 and 1.0>
}
Return one element per candidate in the same order they were listed. If a candidate is not a real violation, set confidence to 0.0 and reasoning to "not a violation"."""


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
    # Matches both 'retryDelay': '27s' and retry_delay { seconds: 27 }
    match = re.search(r"retryDelay['\"]?\s*[:{,]\s*['\"]?(\d+)", str(error_message), re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"seconds:\s*(\d+)", str(error_message))
    if match:
        return float(match.group(1))
    return 0.0


def call_llm(prompt: str) -> Dict[str, object]:
    """Call Gemini API and return a validated SOLID violation analysis as a dict."""
    client = _get_client()
    initial_prompt = f"{prompt}\n\n{_JSON_SCHEMA}"

    last_error = "unknown error"
    for attempt in range(_MAX_RETRIES):
        t_start = time.monotonic()
        print(f"  [LLM] attempt {attempt + 1}/{_MAX_RETRIES} — calling {_MODEL_NAME} ...", flush=True)
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
            elapsed = time.monotonic() - t_start
            print(f"  [LLM] response received in {elapsed:.2f}s", flush=True)

            raw = _strip_fences(response.text)
            data = json.loads(raw)

            if not _validate(data):
                missing = _REQUIRED_FIELDS - set(data.keys()) if isinstance(data, dict) else _REQUIRED_FIELDS
                last_error = f"missing required fields: {missing}"
                print(f"  [LLM] validation failed — {last_error}", flush=True)
                continue

            print(f"  [LLM] OK — confidence={data.get('confidence')}", flush=True)
            return _normalize(data)

        except json.JSONDecodeError as exc:
            elapsed = time.monotonic() - t_start
            last_error = f"invalid JSON — {exc}"
            print(f"  [LLM] JSON parse error after {elapsed:.2f}s — {exc}", flush=True)

        except Exception as exc:
            elapsed = time.monotonic() - t_start
            last_error = str(exc)
            retry_secs = _extract_retry_seconds(last_error)
            is_rate_limit = "429" in last_error or "RESOURCE_EXHAUSTED" in last_error
            is_unavailable = "503" in last_error or "UNAVAILABLE" in last_error
            sleep_secs = retry_secs if retry_secs > 0 else (30 if is_unavailable else 2 ** attempt)
            print(f"  [LLM] API error after {elapsed:.2f}s — {type(exc).__name__}", flush=True)
            if is_rate_limit:
                print(f"  [LLM] rate limited — waiting {sleep_secs:.0f}s before retry ...", flush=True)
            if is_unavailable:
                print(f"  [LLM] server overloaded — waiting {sleep_secs:.0f}s before retry ...", flush=True)
            if attempt < _MAX_RETRIES - 1:
                time.sleep(sleep_secs)

    raise RuntimeError(
        f"Gemini failed to return valid JSON after {_MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


def call_llm_batch(
    file_path: Path,
    candidates: List[Dict[str, Any]],
    source: str,
) -> List[Dict[str, object]]:
    """Call Gemini once for all candidates in a file. Returns one result per candidate."""
    client = _get_client()

    candidate_lines = "\n".join(
        (
            f"  {i+1}. class={c['class']} method={c['method']} "
            f"symbol={c['symbol_name']} lines={c['line_range']} principle={c['principle']}"
            + (
                f"\n      heuristic context: {c['heuristic_summary']}"
                if c.get('heuristic_summary') else ""
            )
        )
        for i, c in enumerate(candidates)
    )
    base_prompt = (
        f"Analyze this Python file for SOLID design principle violations.\n"
        f"file: {file_path}\n\n"
        f"Candidates to evaluate ({len(candidates)} total):\n{candidate_lines}\n\n"
        f"source (first 200 lines):\n{chr(10).join(source.splitlines()[:200])}\n\n"
        f"{_JSON_SCHEMA_BATCH}"
    )

    last_error = "unknown error"
    for attempt in range(_MAX_RETRIES):
        t_start = time.monotonic()
        print(f"  [LLM] attempt {attempt + 1}/{_MAX_RETRIES} — calling {_MODEL_NAME} (batch {len(candidates)}) ...", flush=True)
        try:
            if attempt == 0:
                request = base_prompt
            else:
                request = (
                    f"{base_prompt}\n\n"
                    f"Your previous response was rejected. Reason: {last_error}\n"
                    f"Correct your output and respond with a valid JSON array only."
                )

            response = client.models.generate_content(model=_MODEL_NAME, contents=request)
            elapsed = time.monotonic() - t_start
            print(f"  [LLM] response received in {elapsed:.2f}s", flush=True)

            raw = _strip_fences(response.text)
            data = json.loads(raw)

            if not isinstance(data, list):
                last_error = "expected a JSON array at top level"
                print(f"  [LLM] validation failed — {last_error}", flush=True)
                continue

            if len(data) != len(candidates):
                last_error = f"expected {len(candidates)} items, got {len(data)}"
                print(f"  [LLM] validation failed — {last_error}", flush=True)
                continue

            invalid = [i for i, item in enumerate(data) if not _validate(item)]
            if invalid:
                last_error = f"items at indices {invalid} failed validation"
                print(f"  [LLM] validation failed — {last_error}", flush=True)
                continue

            results = [_normalize(item) for item in data]
            print(f"  [LLM] OK — {len(results)} results, confidences={[r['confidence'] for r in results]}", flush=True)
            return results

        except json.JSONDecodeError as exc:
            elapsed = time.monotonic() - t_start
            last_error = f"invalid JSON — {exc}"
            print(f"  [LLM] JSON parse error after {elapsed:.2f}s — {exc}", flush=True)

        except Exception as exc:
            elapsed = time.monotonic() - t_start
            last_error = str(exc)
            retry_secs = _extract_retry_seconds(last_error)
            is_rate_limit = "429" in last_error or "RESOURCE_EXHAUSTED" in last_error
            is_unavailable = "503" in last_error or "UNAVAILABLE" in last_error
            sleep_secs = retry_secs if retry_secs > 0 else (30 if is_unavailable else 2 ** attempt)
            print(f"  [LLM] API error after {elapsed:.2f}s — {type(exc).__name__}", flush=True)
            if is_rate_limit:
                print(f"  [LLM] rate limited — waiting {sleep_secs:.0f}s before retry ...", flush=True)
            if is_unavailable:
                print(f"  [LLM] server overloaded — waiting {sleep_secs:.0f}s before retry ...", flush=True)
            if attempt < _MAX_RETRIES - 1:
                time.sleep(sleep_secs)

    raise RuntimeError(
        f"Gemini batch failed after {_MAX_RETRIES} attempts. Last error: {last_error}"
    )

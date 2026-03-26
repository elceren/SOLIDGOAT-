# Mock refactor applied for SRP on ModuleLevel.call_llm
import re
from typing import Dict


def _extract_value(prompt: str, field: str, default: str) -> str:
    match = re.search(rf"^{field}:\s*(.+)$", prompt, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return default


def call_llm(prompt: str) -> Dict[str, object]:
    """Return a deterministic mock response for a SOLID violation analysis."""
    file_path = _extract_value(prompt, "file", "unknown.py")
    class_name = _extract_value(prompt, "class", "ModuleLevel")
    method_name = _extract_value(prompt, "method", "unknown_method")
    principle = _extract_value(prompt, "principle", "SRP")

    return {
        "file": file_path,
        "class": class_name,
        "method": method_name,
        "principle": principle,
        "reasoning": (
            f"Mock LLM flagged `{method_name}` in `{class_name}` as a potential "
            f"{principle} violation because the analyzed unit appears to mix multiple responsibilities."
        ),
        "confidence": 0.85,
    }

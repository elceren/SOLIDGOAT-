# Mock refactor applied for SRP on ModuleLevel.apply_refactor
from pathlib import Path
from typing import Dict

from core.llm import call_llm
from utils.file_loader import read_text_file


def _build_refactor_prompt(issue: Dict[str, object], source: str) -> str:
    return "\n".join(
        [
            "Refactor this Python code to reduce the SOLID violation.",
            f"file: {issue['file']}",
            f"class: {issue['class']}",
            f"method: {issue['method']}",
            f"symbol_name: {issue.get('symbol_name', issue['method'])}",
            f"line_range: {issue.get('line_range', 'L1-L1')}",
            f"principle: {issue['principle']}",
            "source:",
            source,
        ]
    )


def apply_refactor(issue: Dict[str, object], repository_path: Path) -> Dict[str, object]:
    target_path = Path(str(issue["file"]))
    if not target_path.is_absolute():
        target_path = repository_path / target_path

    source = read_text_file(target_path)
    if source is None:
        return {
            "success": False,
            "modified_code": "",
            "message": f"Unable to read file for refactoring: {target_path}",
        }

    prompt = _build_refactor_prompt(issue, source)
    llm_response = call_llm(prompt)
    marker = (
        f"# Mock refactor applied for {issue['principle']} on "
        f"{issue['class']}.{issue['method']}\n"
    )

    if source.startswith(marker):
        modified_code = source
    else:
        modified_code = marker + source
        target_path.write_text(modified_code, encoding="utf-8")

    return {
        "success": True,
        "modified_code": modified_code,
        "message": f"Refactoring applied using mock LLM response ({llm_response['confidence']}).",
    }

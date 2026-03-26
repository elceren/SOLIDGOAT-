# Mock refactor applied for SRP on ModuleLevel.test_registry_prevents_duplicates
import json
from pathlib import Path

from config import BASE_DIR
from core.detector import detect_violations
from core.registry import IssueRegistry


def test_detector_finds_mock_issues() -> None:
    issues = detect_violations(BASE_DIR)
    assert issues, "Expected at least one mock issue in the framework repository."
    assert {"file", "class", "method", "principle", "reasoning", "confidence"} <= set(issues[0])
    principles = {issue["principle"] for issue in issues}
    assert principles <= {"SRP", "OCP", "LSP", "ISP", "DIP"}
    assert len(principles) >= 2


def test_registry_prevents_duplicates(tmp_path: Path) -> None:
    registry_path = tmp_path / "issues.json"
    registry = IssueRegistry(registry_path)
    issue = {
        "file": "sample.py",
        "class": "Sample",
        "method": "run",
        "principle": "SRP",
        "reasoning": "mock",
        "confidence": 0.85,
    }

    assert registry.add(issue) is True
    assert registry.add(issue) is False

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(data) == 1

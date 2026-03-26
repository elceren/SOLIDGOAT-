# Mock refactor applied for OCP on IssueRegistry._load
# Mock refactor applied for SRP on IssueRegistry.issue_id
# Mock refactor applied for SRP on IssueRegistry.__init__
import json
from pathlib import Path
from typing import Dict, List, Tuple


class IssueRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._issues = self._load()

    def _load(self) -> List[Dict[str, object]]:
        if not self.registry_path.exists():
            self.registry_path.write_text("[]", encoding="utf-8")
            return []

        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.registry_path.write_text("[]", encoding="utf-8")
            return []

        if isinstance(data, list):
            return data
        return []

    @staticmethod
    def issue_id(issue: Dict[str, object]) -> Tuple[str, str, str]:
        return (
            str(issue.get("principle", "")),
            str(issue.get("file", "")),
            str(issue.get("method", "")),
        )

    def is_duplicate(self, issue: Dict[str, object]) -> bool:
        target_id = self.issue_id(issue)
        return any(self.issue_id(existing) == target_id for existing in self._issues)

    def add(self, issue: Dict[str, object]) -> bool:
        if self.is_duplicate(issue):
            return False

        self._issues.append(issue)
        self.registry_path.write_text(
            json.dumps(self._issues, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return True

    @property
    def issues(self) -> List[Dict[str, object]]:
        return list(self._issues)

# Mock refactor applied for SRP on ModuleLevel.main
import sys
from pathlib import Path

from config import DEFAULT_REPOSITORY, ISSUES_PATH
from core.detector import detect_violations
from core.refactor import apply_refactor
from core.registry import IssueRegistry
from runners.test_runner import run_tests
from utils.logger import log


def main() -> int:
    repository_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_REPOSITORY
    registry = IssueRegistry(ISSUES_PATH)

    log(f"Scanning repository: {repository_path}")
    issues = detect_violations(repository_path)
    log(f"Detected issues: {len(issues)}")

    if not issues:
        log("No issues detected.")
        return 0

    for index, issue in enumerate(issues, start=1):
        duplicate = registry.is_duplicate(issue)
        status = "duplicate" if duplicate else "new"
        log(
            f"Issue {index}: {issue['principle']} in {issue['file']} "
            f"({issue.get('symbol_name', issue['class'] + '.' + issue['method'])}, "
            f"{issue.get('line_range', 'L1-L1')}) -> {status}"
        )

        if duplicate:
            continue

        registry.add(issue)
        refactor_result = apply_refactor(issue, repository_path)
        log(f"Refactoring step: {'executed' if refactor_result['success'] else 'failed'}")
        log(refactor_result["message"])

        tests_passed, test_output = run_tests(repository_path)
        log(f"Tests: {'passed' if tests_passed else 'failed'}")
        print(test_output or "No test output captured.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

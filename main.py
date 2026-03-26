import argparse
import sys
from pathlib import Path

from config import DEFAULT_REPOSITORY, ISSUES_PATH, SOLID_PRINCIPLES
from core.detector import detect_violations
from core.refactor import apply_refactor
from core.registry import IssueRegistry
from runners.test_runner import run_tests
from utils.artifacts import (
    build_pr_report,
    create_manual_review_queue,
    create_run_directory,
    write_json,
    write_text,
)
from utils.logger import log


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SOLID detection/refactor pipeline.")
    parser.add_argument("repository", nargs="?", default=str(DEFAULT_REPOSITORY))
    parser.add_argument(
        "--principle",
        choices=SOLID_PRINCIPLES,
        help="Run a single-principle scan instead of all five principles.",
    )
    parser.add_argument(
        "--max-refactors",
        type=int,
        default=2,
        help="Maximum number of new issues to refactor in this run.",
    )
    parser.add_argument(
        "--test-target",
        action="append",
        default=[],
        help="Optional pytest target. Repeat to pass multiple targets.",
    )
    parser.add_argument(
        "--scan-root",
        action="append",
        default=[],
        help="Optional relative path inside the repository to restrict detection scope.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    repository_path = Path(args.repository).resolve()
    registry = IssueRegistry(ISSUES_PATH)
    run_dir = create_run_directory(repository_path)
    principles = [args.principle] if args.principle else list(SOLID_PRINCIPLES)
    scan_roots = [repository_path / root for root in args.scan_root] if args.scan_root else None
    baseline_success, baseline_output = run_tests(repository_path, args.test_target)
    baseline_tests = {"success": baseline_success, "output": baseline_output}
    write_json(run_dir / "baseline_tests.json", baseline_tests)

    log(f"Scanning repository: {repository_path}")
    log(f"Baseline tests: {'passed' if baseline_success else 'failed'}")

    all_issues: list[dict[str, object]] = []
    scan_summaries: list[dict[str, object]] = []
    refactor_attempts: list[dict[str, object]] = []
    refactor_budget = max(args.max_refactors, 0)

    for principle in principles:
        issues = detect_violations(repository_path, principle=principle, scan_roots=scan_roots)
        write_json(run_dir / f"detections_{principle}.json", issues)
        duplicates = sum(1 for issue in issues if registry.is_duplicate(issue))
        new_count = len(issues) - duplicates
        scan_summary = {
            "principle": principle,
            "issue_count": len(issues),
            "new_count": new_count,
            "duplicate_count": duplicates,
        }
        scan_summaries.append(scan_summary)
        all_issues.extend(issues)
        log(
            f"{principle} scan: {len(issues)} detections "
            f"({new_count} new, {duplicates} duplicates)"
        )

        for issue in issues:
            duplicate = registry.is_duplicate(issue)
            status = "duplicate" if duplicate else "new"
            log(
                f"Issue: {issue['principle']} in {issue['file']} "
                f"({issue.get('symbol_name', issue['class'] + '.' + issue['method'])}, "
                f"{issue.get('line_range', 'L1-L1')}) -> {status}"
            )

            if duplicate or refactor_budget <= 0:
                continue

            registry.add(issue)
            refactor_result = apply_refactor(issue, repository_path)
            tests_passed, test_output = run_tests(repository_path, args.test_target)
            attempt = {
                "issue": issue,
                "refactor": refactor_result,
                "tests": {"success": tests_passed, "output": test_output},
            }
            refactor_attempts.append(attempt)
            refactor_budget -= 1
            log(f"Refactoring step: {'executed' if refactor_result['success'] else 'failed'}")
            log(refactor_result["message"])
            log(f"Tests after refactor: {'passed' if tests_passed else 'failed'}")

    review_queue = create_manual_review_queue(all_issues)
    write_json(run_dir / "scan_summary.json", scan_summaries)
    write_json(run_dir / "manual_review_queue.json", review_queue)
    write_json(run_dir / "refactor_attempts.json", refactor_attempts)
    write_text(
        run_dir / "pr_report.md",
        build_pr_report(repository_path, scan_summaries, review_queue, refactor_attempts, baseline_tests),
    )

    if not all_issues:
        log("No issues detected.")
        return 0

    log(f"Artifacts written to: {run_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

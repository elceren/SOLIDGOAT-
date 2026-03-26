import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import RUNS_DIR


def create_run_directory(repository_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_name = repository_path.name.replace(" ", "_")
    run_dir = RUNS_DIR / f"{timestamp}_{repo_name}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_manual_review_queue(issues: List[Dict[str, object]], limit: int = 3) -> List[Dict[str, object]]:
    queue: List[Dict[str, object]] = []
    for issue in issues[:limit]:
        queue.append(
            {
                "issue_id": {
                    "principle": issue["principle"],
                    "file": issue["file"],
                    "symbol_name": issue.get("symbol_name", issue["method"]),
                    "line_range": issue.get("line_range", "L1-L1"),
                },
                "status": "pending_manual_review",
                "reviewer": "",
                "notes": "",
            }
        )
    return queue


def build_pr_report(
    repository_path: Path,
    scans: List[Dict[str, object]],
    selected_reviews: List[Dict[str, object]],
    refactors: List[Dict[str, object]],
    baseline_tests: Optional[Dict[str, object]],
) -> str:
    lines = [
        f"# Trial Report for {repository_path.name}",
        "",
        f"Repository: `{repository_path}`",
        "",
        "## Scan Summary",
    ]

    for scan in scans:
        lines.append(
            f"- {scan['principle']}: {scan['issue_count']} detections "
            f"({scan['new_count']} new, {scan['duplicate_count']} duplicates)"
        )

    lines.extend(
        [
            "",
            "## Baseline Tests",
            f"- Success: {baseline_tests['success'] if baseline_tests else 'not run'}",
        ]
    )

    lines.extend(["", "## Manual Review Queue"])
    if selected_reviews:
        for review in selected_reviews:
            issue_id = review["issue_id"]
            lines.append(
                f"- {issue_id['principle']} in `{issue_id['file']}` "
                f"at `{issue_id['symbol_name']}` ({issue_id['line_range']}) "
                f"-> {review['status']}"
            )
    else:
        lines.append("- No issues selected for review.")

    lines.extend(["", "## Refactor Attempts"])
    if refactors:
        for attempt in refactors:
            issue = attempt["issue"]
            lines.append(
                f"- {issue['principle']} / {issue.get('symbol_name', issue['method'])} "
                f"-> refactor {'succeeded' if attempt['refactor']['success'] else 'failed'}, "
                f"tests {'passed' if attempt['tests']['success'] else 'failed'}"
            )
    else:
        lines.append("- No refactor attempts executed.")

    return "\n".join(lines) + "\n"

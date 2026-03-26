import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_tests(repository_path: Path, targets: List[str] | None = None) -> Tuple[bool, str]:
    command = [sys.executable, "-m", "pytest", "-o", "addopts="]
    if targets:
        command.extend(targets)
    completed = subprocess.run(
        command,
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode == 0, output

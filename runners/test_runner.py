import subprocess
import sys
from pathlib import Path
from typing import Tuple


def run_tests(repository_path: Path) -> Tuple[bool, str]:
    command = [sys.executable, "-m", "pytest"]
    completed = subprocess.run(
        command,
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode == 0, output

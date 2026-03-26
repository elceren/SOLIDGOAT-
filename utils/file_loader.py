from pathlib import Path
from typing import Optional


def read_text_file(path: Path) -> Optional[str]:
    """Read a text file safely and return None on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

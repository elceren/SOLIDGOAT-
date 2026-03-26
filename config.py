from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ISSUES_PATH = DATA_DIR / "issues.json"
DEFAULT_REPOSITORY = BASE_DIR
SUPPORTED_EXTENSIONS = {".py"}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "venv",
    ".venv",
}

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_URL_PREFIX = "/uploads"
MAX_UPLOAD_SIZE = 20 * 1024 * 1024


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def build_upload_url(stored_name: str) -> str:
    return f"{UPLOAD_URL_PREFIX}/{stored_name}"

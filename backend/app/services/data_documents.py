import re
import unicodedata
from pathlib import Path

from app.core.config import BACKEND_DIR


DATA_DIR = BACKEND_DIR / "data"
SUPPORTED_DATA_EXTENSIONS = {".txt", ".md", ".docx"}


def normalize_text(value: str) -> str:
    ascii_text = "".join(
        char for char in unicodedata.normalize("NFD", value.casefold()) if unicodedata.category(char) != "Mn"
    )
    ascii_text = ascii_text.replace("\u0111", "d")
    ascii_text = re.sub(r"[^a-z0-9]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def resolve_data_document(filename: str) -> Path | None:
    requested = (DATA_DIR / filename).resolve()
    data_root = DATA_DIR.resolve()
    if data_root not in requested.parents or not requested.is_file():
        return None
    if requested.suffix.lower() not in SUPPORTED_DATA_EXTENSIONS:
        return None
    return requested


def search_data_documents(query: str, limit: int = 50) -> list[dict]:
    normalized_keyword = normalize_text(query.strip())
    if not normalized_keyword or not DATA_DIR.exists():
        return []

    matches = []
    for path in DATA_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_DATA_EXTENSIONS:
            continue

        normalized_name = normalize_text(path.stem)
        normalized_filename = normalize_text(path.name)
        if normalized_keyword not in normalized_name and normalized_keyword not in normalized_filename:
            continue

        if normalized_name == normalized_keyword:
            score = 0
        elif normalized_name.startswith(normalized_keyword):
            score = 1
        elif normalized_filename.startswith(normalized_keyword):
            score = 2
        else:
            score = 3
        matches.append((score, normalized_name, path))

    results = []
    for _, _, path in sorted(matches)[:limit]:
        results.append(
            {
                "id": path.name,
                "title": path.stem,
                "filename": path.name,
                "size": path.stat().st_size,
            }
        )

    return results

import re


CHAPTER_RE = re.compile(r"^\s*chương\s+([ivxlcdm]+|\d+)\b.*", re.IGNORECASE)
ARTICLE_RE = re.compile(r"^\s*điều\s+\d+[a-zA-Z]?\.\s+.+", re.IGNORECASE)
CLAUSE_RE = re.compile(r"^\s*(\d{1,2})\.\s+.+")
POINT_RE = re.compile(r"^\s*([a-zđ])[\)\.]\s+.+", re.IGNORECASE)


def is_chapter(line: str) -> bool:
    return bool(CHAPTER_RE.match(line.strip()))


def is_article(line: str) -> bool:
    return bool(ARTICLE_RE.match(line.strip()))


def is_clause(line: str) -> bool:
    return bool(CLAUSE_RE.match(line.strip()))


def is_point(line: str) -> bool:
    return bool(POINT_RE.match(line.strip()))


def chunk_by_header(text: str, max_chars: int = 1200) -> list[dict]:
    lines = [line.rstrip() for line in text.splitlines()]

    chunks: list[dict] = []

    current_chapter = None
    current_article = None
    current_clause = None
    current_point = None
    current_lines: list[str] = []

    def build_header() -> str:
        parts = []

        if current_chapter:
            parts.append(current_chapter)

        if current_article:
            parts.append(current_article)

        if current_clause:
            match = CLAUSE_RE.match(current_clause)
            if match:
                parts.append(f"Khoản {match.group(1)}")

        if current_point:
            match = POINT_RE.match(current_point)
            if match:
                parts.append(f"Điểm {match.group(1)}")

        return " > ".join(parts) if parts else "General"

    def split_content(content: str) -> list[str]:
        if len(content) <= max_chars:
            return [content]

        result = []
        start = 0

        while start < len(content):
            end = start + max_chars
            part = content[start:end].strip()
            if part:
                result.append(part)
            start = end

        return result

    def flush():
        nonlocal current_lines

        content = "\n".join(line for line in current_lines if line.strip()).strip()

        if not content:
            current_lines = []
            return

        header = build_header()

        for part in split_content(content):
            chunks.append(
                {
                    "header": header,
                    "chapter": current_chapter,
                    "article": current_article,
                    "clause": current_clause,
                    "point": current_point,
                    "text": part,
                }
            )

        current_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            current_lines.append(line)
            continue

        if is_chapter(stripped):
            flush()
            current_chapter = stripped
            current_article = None
            current_clause = None
            current_point = None
            continue

        if is_article(stripped):
            flush()
            current_article = stripped
            current_clause = None
            current_point = None
            current_lines = []
            continue

        if is_clause(stripped):
            flush()
            current_clause = stripped
            current_point = None
            current_lines = [stripped]
            continue

        if is_point(stripped):
            flush()
            current_point = stripped
            current_lines = [stripped]
            continue

        current_lines.append(line)

    flush()
    return chunks
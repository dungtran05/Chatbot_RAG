import re


HEADER_PATTERNS = [
    re.compile(r"^(#{1,6})\s+.+"),
    re.compile(r"^\d+(\.\d+)*\s+.+"),
    re.compile(r"^[A-Z][A-Z0-9\s\-/,:]{5,}$"),
]


def is_header(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return any(pattern.match(stripped) for pattern in HEADER_PATTERNS)


def chunk_by_header(text: str, max_chars: int = 1200) -> list[dict]:
    lines = [line.rstrip() for line in text.splitlines()]
    chunks: list[dict] = []
    current_header = "General"
    current_lines: list[str] = []

    def flush():
        nonlocal current_lines
        content = "\n".join(line for line in current_lines if line.strip()).strip()
        if not content:
            current_lines = []
            return
        if len(content) <= max_chars:
            chunks.append({"header": current_header, "text": content})
        else:
            for i in range(0, len(content), max_chars):
                chunks.append({"header": current_header, "text": content[i : i + max_chars]})
        current_lines = []

    for line in lines:
        if is_header(line):
            flush()
            current_header = line.strip()
            continue
        current_lines.append(line)
    flush()
    return chunks


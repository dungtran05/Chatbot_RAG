from pathlib import Path

from app.services.ocr import pdf_ocr_service


def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return pdf_ocr_service.extract_text(file_bytes)
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


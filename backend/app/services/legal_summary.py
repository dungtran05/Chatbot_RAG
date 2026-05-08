from pathlib import Path

import google.generativeai as genai

from app.core.config import settings
from app.services.file_parser import extract_text_from_upload


SUPPORTED_SUMMARY_EXTENSIONS = {".txt", ".docx"}
MAX_SUMMARY_INPUT_CHARS = 24000


def can_summarize_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_SUMMARY_EXTENSIONS


def summarize_legal_text(filename: str, file_bytes: bytes) -> str:
    if not can_summarize_file(filename):
        return ""

    text = extract_text_from_upload(filename, file_bytes).strip()
    if not text:
        return ""

    model = genai.GenerativeModel(settings.gemini_model)
    prompt = f"""
Bạn là trợ lý pháp luật tiếng Việt. Hãy tóm tắt văn bản pháp luật được người dùng tải lên.

Yêu cầu:
- Viết tiếng Việt rõ ràng, dễ hiểu.
- Nêu tên/chủ đề văn bản nếu xác định được.
- Tóm tắt các nội dung chính, quyền/nghĩa vụ, thời hạn, chế tài hoặc điểm cần chú ý.
- Không bịa thông tin ngoài văn bản.
- Định dạng markdown ngắn gọn.

Tên file: {filename}

Nội dung:
{text[:MAX_SUMMARY_INPUT_CHARS]}
"""
    response = model.generate_content(prompt)
    return (response.text or "").strip()

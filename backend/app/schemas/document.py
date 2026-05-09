from pydantic import BaseModel


# Dữ liệu tài liệu trả về frontend sau khi upload hoặc list documents.
class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    uploaded_at: str
    chunk_count: int


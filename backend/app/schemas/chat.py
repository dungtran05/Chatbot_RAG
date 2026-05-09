from pydantic import BaseModel, Field


# Request frontend gửi khi người dùng đặt câu hỏi.
class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


# Một nguồn tham khảo được lấy từ tài liệu hoặc web fallback.
class CitationItem(BaseModel):
    index: int
    source: str | None = None
    header: str | None = None
    source_type: str


# Metadata mô tả quá trình retrieval để frontend/debug có thể hiển thị.
class RetrievalMetadata(BaseModel):
    generated_queries: list[str]
    total_contexts: int
    used_web_fallback: bool


# Metadata về model trả lời và conversation được cập nhật.
class ChatMetadata(BaseModel):
    model: str
    conversation_id: str


# Response đầy đủ của API chat.
class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    retrieval: RetrievalMetadata
    metadata: ChatMetadata

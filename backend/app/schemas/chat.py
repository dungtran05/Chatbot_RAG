from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class CitationItem(BaseModel):
    index: int
    source: str | None = None
    header: str | None = None
    source_type: str


class RetrievalMetadata(BaseModel):
    generated_queries: list[str]
    total_contexts: int
    used_web_fallback: bool


class ChatMetadata(BaseModel):
    model: str
    conversation_id: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationItem]
    retrieval: RetrievalMetadata
    metadata: ChatMetadata

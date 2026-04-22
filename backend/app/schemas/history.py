from pydantic import BaseModel


class MessageItem(BaseModel):
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    updated_at: str
    messages: list[MessageItem]


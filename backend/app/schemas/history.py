from pydantic import BaseModel


# Một tin nhắn trong lịch sử trò chuyện.
class MessageItem(BaseModel):
    role: str
    content: str
    created_at: str


# Một cuộc trò chuyện gồm tiêu đề, thời gian cập nhật và danh sách tin nhắn.
class ConversationResponse(BaseModel):
    id: str
    title: str
    updated_at: str
    messages: list[MessageItem]


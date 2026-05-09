from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = BASE_DIR / "backend"


class Settings(BaseSettings):
    # Đọc cấu hình từ file backend/.env và bỏ qua biến thừa nếu có.
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Cấu hình chung của ứng dụng và JWT.
    app_name: str = Field(default="rag-chatbot", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")
    secret_key: str = Field(alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Cấu hình MongoDB dùng để lưu user, tài liệu và lịch sử chat.
    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db: str = Field(alias="MONGODB_DB")

    # Cấu hình Qdrant dùng để lưu và tìm kiếm vector tài liệu.
    qdrant_url: str = Field(alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(alias="QDRANT_COLLECTION")

    # Cấu hình model Gemini dùng để sinh câu trả lời.
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    # Tavily dùng làm web search fallback khi tài liệu nội bộ chưa đủ context.
    tavily_api_key: str | None = Field(default=None, alias="TAVILY_API_KEY")
    tavily_max_results: int = Field(default=5, alias="TAVILY_MAX_RESULTS")

    # Model embedding và rerank phục vụ quá trình tìm kiếm tài liệu.
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    rerank_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="RERANK_MODEL")

    # Cấu hình thư mục upload và giới hạn dung lượng file.
    upload_dir: str = Field(default="backend/storage/uploads", alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=25, alias="MAX_UPLOAD_SIZE_MB")

    @property
    def upload_path(self) -> Path:
        # Tạo thư mục upload nếu chưa tồn tại, rồi trả về đường dẫn tuyệt đối.
        path = BASE_DIR / self.upload_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    # Cache settings để không phải đọc .env nhiều lần.
    return Settings()


# Biến settings dùng chung trong toàn backend.
settings = get_settings()

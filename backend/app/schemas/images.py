from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ImageUploadResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    original_name: str
    content_hash: str
    mime_type: str
    format: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    channels: int = Field(gt=0)
    color_mode: str
    size_bytes: int = Field(gt=0)
    created_at: datetime
    expires_at: datetime
    content_url: str

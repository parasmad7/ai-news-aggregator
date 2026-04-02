from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class AnthropicPost(BaseModel):
    """Represents a single blog post or news item from Anthropic."""
    title: str
    url: HttpUrl
    description: str
    published_at: datetime
    category: Optional[str] = None
    content: Optional[str] = None

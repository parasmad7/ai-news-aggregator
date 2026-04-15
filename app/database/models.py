from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from datetime import datetime
from .session import Base

class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    author = Column(String, nullable=False)
    transcript = Column(Text, nullable=True)

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    source = Column(String, nullable=False) # OpenAI, Anthropic
    content = Column(Text, nullable=True)

class DigestModel(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    source_type = Column(String, nullable=False) # 'video' or 'post'
    published_at = Column(DateTime, nullable=False)
    relevance_score = Column(Float, nullable=True)
    relevance_reason = Column(Text, nullable=True)
    is_sent = Column(Boolean, default=False)

class EmailModel(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

from sqlalchemy import Column, Integer, String, DateTime, Text
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

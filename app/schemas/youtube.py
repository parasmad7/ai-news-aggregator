from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional

class YouTubeVideo(BaseModel):
    """Represents metadata for a single YouTube video."""
    title: str
    video_id: str
    url: HttpUrl
    published_at: datetime
    author: str
    transcript: Optional[str] = None

class ChannelVideos(BaseModel):
    """Represents a collection of videos from a YouTube channel."""
    channel_id: str
    videos: List[YouTubeVideo]

class VideoTranscript(BaseModel):
    """Represents the transcript content for a specific YouTube video."""
    video_id: str
    transcript: str

from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import VideoModel, PostModel
from app.schemas.youtube import YouTubeVideo
from app.schemas.openai import OpenAIPost
from app.schemas.anthropic import AnthropicPost

class NewsRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_video(self, video: YouTubeVideo):
        """Adds or updates a YouTube video in the database."""
        db_video = self.db.query(VideoModel).filter(VideoModel.video_id == video.video_id).first()
        
        if db_video:
            db_video.title = video.title
            db_video.url = str(video.url)
            db_video.published_at = video.published_at
            db_video.author = video.author
            db_video.transcript = video.transcript
        else:
            db_video = VideoModel(
                video_id=video.video_id,
                title=video.title,
                url=str(video.url),
                published_at=video.published_at,
                author=video.author,
                transcript=video.transcript
            )
            self.db.add(db_video)
        
        self.db.commit()
        return db_video

    def upsert_post(self, post: OpenAIPost | AnthropicPost, source: str):
        """Adds or updates a blog post in the database."""
        db_post = self.db.query(PostModel).filter(PostModel.url == str(post.url)).first()
        
        if db_post:
            db_post.title = post.title
            db_post.description = post.description
            db_post.published_at = post.published_at
            db_post.category = post.category
            db_post.source = source
            db_post.content = post.content
        else:
            db_post = PostModel(
                url=str(post.url),
                title=post.title,
                description=post.description,
                published_at=post.published_at,
                category=post.category,
                source=source,
                content=post.content
            )
            self.db.add(db_post)
        
        self.db.commit()
        return db_post

    def truncate_posts(self):
        """Clears all entries from the posts table."""
        self.db.query(PostModel).delete()
        self.db.commit()

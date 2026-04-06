from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from .models import VideoModel, PostModel, DigestModel, EmailModel
from app.schemas.youtube import YouTubeVideo
from app.schemas.openai import OpenAIPost
from app.schemas.anthropic import AnthropicPost

class NewsRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_video(self, video: YouTubeVideo):
        """Adds a YouTube video to the database if it doesn't already exist."""
        db_video = self.db.query(VideoModel).filter(VideoModel.video_id == video.video_id).first()
        
        if not db_video:
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

    def add_post(self, post: OpenAIPost | AnthropicPost, source: str):
        """Adds a blog post to the database if it doesn't already exist."""
        db_post = self.db.query(PostModel).filter(PostModel.url == str(post.url)).first()
        
        if not db_post:
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

    def get_all_videos(self):
        """Fetches all videos from the database."""
        return self.db.query(VideoModel).all()

    def get_all_posts(self):
        """Fetches all posts from the database."""
        return self.db.query(PostModel).all()

    def get_digest_by_url(self, url: str):
        """Fetches a digest by its source URL."""
        return self.db.query(DigestModel).filter(DigestModel.source_url == url).first()

    def create_digest(self, url: str, title: str, summary: str, source_type: str, published_at: datetime) -> DigestModel:
        """Creates a digest for a video or post."""
        digest = DigestModel(
            source_url=url,
            title=title,
            summary=summary,
            source_type=source_type,
            published_at=published_at
        )
        self.db.add(digest)
        self.db.commit()
        self.db.refresh(digest)
        return digest

    def get_unranked_digests(self):
        """Fetches all digests that haven't been ranked yet."""
        return self.db.query(DigestModel).filter(DigestModel.relevance_score == None).all()

    def update_digest_relevance(self, digest_id: int, score: float, reason: str):
        """Updates the relevance score and reason for a digest."""
        db_digest = self.db.query(DigestModel).filter(DigestModel.id == digest_id).first()
        if db_digest:
            db_digest.relevance_score = score
            db_digest.relevance_reason = reason
            self.db.commit()
        return db_digest

    def get_top_digests(self, limit: int = 10):
        """Fetches the top N digests ranked by relevance score."""
        return self.db.query(DigestModel).order_by(DigestModel.relevance_score.desc()).limit(limit).all()

    def create_email(self, subject: str, body: str):
        """Stores a generated email template in the database."""
        db_email = EmailModel(
            subject=subject,
            body=body,
            created_at=datetime.utcnow()
        )
        self.db.add(db_email)
        self.db.commit()
        return db_email

    def update_email_sent_status(self, email_id: int):
        """Marks an email as sent by updating sent_at."""
        db_email = self.db.query(EmailModel).filter(EmailModel.id == email_id).first()
        if db_email:
            db_email.sent_at = datetime.utcnow()
            self.db.commit()
        return db_email

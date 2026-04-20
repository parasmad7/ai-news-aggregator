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
        """Adds a YouTube video to the database if it doesn't already exist. Returns (video, created)."""
        db_video = self.db.query(VideoModel).filter(VideoModel.video_id == video.video_id).first()
        created = False
        
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
            created = True
        
        return db_video, created

    def add_post(self, post: OpenAIPost | AnthropicPost, source: str):
        """Adds a blog post to the database if it doesn't already exist. Returns (post, created)."""
        db_post = self.db.query(PostModel).filter(PostModel.url == str(post.url)).first()
        created = False
        
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
            created = True
        
        return db_post, created

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
        """Creates a digest for a video or post if it doesn't already exist."""
        db_digest = self.db.query(DigestModel).filter(DigestModel.source_url == url).first()
        
        if not db_digest:
            db_digest = DigestModel(
                source_url=url,
                title=title,
                summary=summary,
                source_type=source_type,
                published_at=published_at
            )
            self.db.add(db_digest)
            self.db.commit()
            self.db.refresh(db_digest)
        
        return db_digest

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

    def get_top_digests(self, limit: int = 10, hours: int = None, unsent_only: bool = True):
        """Fetches the top N digests ranked by relevance score, optionally filtered by the last N hours."""
        query = self.db.query(DigestModel)
        
        if unsent_only:
            query = query.filter(DigestModel.is_sent == False)

        if hours:
            from datetime import timedelta
            threshold = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(DigestModel.published_at >= threshold)
            
        return query.order_by(DigestModel.relevance_score.desc()).limit(limit).all()

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
        """Marks an email record as sent by updating sent_at."""
        db_email = self.db.query(EmailModel).filter(EmailModel.id == email_id).first()
        if db_email:
            db_email.sent_at = datetime.utcnow()
            self.db.commit()
        return db_email

    def mark_digests_as_sent(self, digest_ids: list[int]):
        """Marks a list of digests as sent."""
        self.db.query(DigestModel).filter(DigestModel.id.in_(digest_ids)).update({"is_sent": True}, synchronize_session=False)
        self.db.commit()

    def get_detailed_state(self):
        """Returns a snapshot of the current state of the news pipeline including headlines."""
        from datetime import timedelta
        threshold_72h = datetime.utcnow() - timedelta(hours=72)
        
        # 1. Pending Summaries (Titles)
        digested_urls_stmt = select(DigestModel.source_url)
        pending_videos = self.db.query(VideoModel).filter(~VideoModel.url.in_(digested_urls_stmt)).limit(10).all()
        pending_posts = self.db.query(PostModel).filter(~PostModel.url.in_(digested_urls_stmt)).limit(10).all()
        
        pending_summary_titles = [v.title for v in pending_videos] + [p.title for p in pending_posts]
        
        # 2. Pending Curation (Titles)
        unranked_digests = self.db.query(DigestModel).filter(DigestModel.relevance_score == None).limit(10).all()
        pending_curation_titles = [d.title for d in unranked_digests]
        
        # 3. Ready for Email (Titles + Scores)
        ready_digests = self.db.query(DigestModel).filter(
            DigestModel.relevance_score >= 0.7, 
            DigestModel.is_sent == False,
            DigestModel.published_at >= threshold_72h
        ).order_by(DigestModel.relevance_score.desc()).limit(10).all()
        ready_email_titles = [f"{d.title} (Score: {d.relevance_score})" for d in ready_digests]
        
        # 4. Last email sent time
        last_email = self.db.query(EmailModel).filter(EmailModel.sent_at != None).order_by(EmailModel.sent_at.desc()).first()
        last_email_time = last_email.sent_at if last_email else None
        
        return {
            "pending_summaries_count": len(pending_summary_titles),
            "pending_summaries": pending_summary_titles[:10],
            "pending_curation_count": self.db.query(DigestModel).filter(DigestModel.relevance_score == None).count(),
            "pending_curation": pending_curation_titles,
            "ready_email_count": self.db.query(DigestModel).filter(
                DigestModel.relevance_score >= 0.7, 
                DigestModel.is_sent == False,
                DigestModel.published_at >= threshold_72h
            ).count(),
            "ready_email_items": ready_email_titles,
            "last_email_at": last_email_time
        }

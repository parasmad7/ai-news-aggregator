import sys
from pathlib import Path
# Add the project root to sys.path for absolute imports to works
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import feedparser
import requests
import re
import json
from datetime import datetime, timezone, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
from app.schemas.youtube import YouTubeVideo, ChannelVideos

class YouTubeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })

    def _fetch_rss(self, channel_id: str) -> List[Dict]:
        try:
            resp = self.session.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}", timeout=10)
            if resp.status_code != 200: return []
            feed = feedparser.parse(resp.text)
            return [{
                'title': e.title, 'video_id': self._extract_id(e.link), 'author': e.author,
                'published_at': datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
            } for e in feed.entries if self._extract_id(e.link)]
        except: return []

    def _fetch_html(self, channel_id: str) -> List[Dict]:
        try:
            print(f"RSS failed for {channel_id}, trying HTML fallback...")
            resp = self.session.get(f"https://www.youtube.com/channel/{channel_id}/videos", timeout=10)
            match = re.search(r'var ytInitialData = (\{.*?\});', resp.text)
            if not match: return []
            
            data = json.loads(match.group(1))
            tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            videos_tab = next(t for t in tabs if t.get('tabRenderer', {}).get('title') in ('Videos', 'Uploads'))
            items = videos_tab['tabRenderer']['content']['richGridRenderer']['contents']
            
            entries = []
            for i in items:
                if 'richItemRenderer' not in i: continue
                v = i['richItemRenderer']['content']['videoRenderer']
                entries.append({
                    'title': v['title']['runs'][0]['text'],
                    'video_id': v['videoId'],
                    'published_at': self._parse_time(v.get('publishedTimeText', {}).get('simpleText', '')),
                    'author': 'Channel'
                })
            return entries
        except: return []

    def _parse_time(self, text: str) -> datetime:
        now = datetime.now(timezone.utc)
        m = re.search(r'(\d+)\s+(second|minute|hour|day|week|month|year)', text)
        if not m: return now
        val, unit = int(m.group(1)), m.group(2)
        mapping = {'second': 'seconds', 'minute': 'minutes', 'hour': 'hours', 'day': 'days', 'week': 'weeks'}
        if unit in mapping: return now - timedelta(**{mapping[unit]: val})
        if unit == 'month': return now - timedelta(days=val * 30)
        return now - timedelta(days=val * 365)

    def _extract_id(self, url: str) -> Optional[str]:
        m = re.search(r'(?:v=|\/|be\/)([0-9A-Za-z_-]{11})', url)
        return m.group(1) if m else None

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetches the transcript for a video, trying English first, then Hindi."""
        try:
            # Try English first, then Hindi
            segments = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'hi'])
            return " ".join([s.text.replace('\n', ' ') for s in segments])
        except Exception as e:
            print(f"  -> Transcript failed for {video_id}: {e}")
            return None

    def get_latest_videos(self, channel_id: str, max_age_hours: int = 24) -> List[Dict]:
        """Fetches metadata for the latest videos. Transcripts are NOT fetched here for efficiency."""
        threshold = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        raw_videos = self._fetch_rss(channel_id) or self._fetch_html(channel_id)
        
        recent_videos = []
        for v in raw_videos:
            if v['published_at'] >= threshold:
                recent_videos.append(v)
        return recent_videos

if __name__ == "__main__":
    cid = input("Enter YouTube Channel ID: ").strip()
    if cid:
        channel_data = YouTubeScraper().get_latest_videos(cid, 24)
        if not channel_data.videos:
            print("\nNo recent videos found.")
        else:
            for i, v in enumerate(channel_data.videos, 1):
                print(f"\n--- Video {i} ---\nTitle: {v.title}\nURL:   {v.url}\nDate:  {v.published_at}\nTranscript: {len(v.transcript or '')} chars")

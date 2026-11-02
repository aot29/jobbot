from jobbot.interfaces import JobFetcher
import feedparser


class TuBerlinFetcher(JobFetcher):
    """Fetch jobs from TU Berlin RSS feed."""

    def __init__(self):
        self.FEED_URL = "https://www.jobs.tu-berlin.de/stellenausschreibungen.atom"

    def fetch(self) -> list[dict]:
        feed = feedparser.parse(self.FEED_URL)
        jobs = []
        for entry in feed.entries:
            jobs.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "description": entry.get("description", "") or entry.get("summary", ""),
                "published": entry.get("published", ""),
                "id": entry.get("id", ""),
            })
        return jobs

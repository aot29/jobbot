from jobbot.interfaces import JobFetcher
import feedparser


class FuBerlinFetcher(JobFetcher):
    """Fetch jobs from FU Berlin RSS feed."""

    def __init__(self):
        self.FEED_URL = "https://www.fu-berlin.de/universitaet/beruf-karriere/jobs/wiss/gesamtliste/index.rss"

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

from jobbot.interfaces import JobFetcher
import feedparser


class BhtFetcher(JobFetcher):
    """Fetch jobs from BHT Berlin RSS feed."""

    def __init__(self):
        self.FEED_URL = "https://stellenticket.bht-berlin.de/en/job-offers.atom"

    def fetch(self) -> list[dict]:
        feed = feedparser.parse(self.FEED_URL)
        jobs = []
        for entry in feed.entries:
            # Extract author/company from feed if available
            company = ""
            if hasattr(entry, "authors"):
                company = entry.authors[0].get("name", "") if entry.authors else ""
            elif hasattr(entry, "author"):
                company = entry.author.get("name", entry.author) if entry.author else ""
            
            # Extract location from custom fields if available
            location = entry.get("location", "") or entry.get("where", "")
            
            jobs.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "description": entry.get("description", "") or entry.get("summary", ""),
                "published": entry.get("published", ""),
                "id": entry.get("id", ""),
                "company": company,
                "location": location,
            })
        return jobs

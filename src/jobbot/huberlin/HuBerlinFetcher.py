from jobbot.interfaces import JobFetcher
import feedparser
import html
import re


class HuBerlinFetcher(JobFetcher):
    """Fetch jobs from the HU Berlin Stellenticket portal.

    The portal publishes all offers as an Atom feed whose entries carry
    the full posting content, so no per-job page scraping is required.
    Each entry title ends with the employer in parentheses, and the
    content contains "Arbeitgeber:"/"Arbeitsort:" fact lines.
    """

    FEED_URL = "https://hu-berlin.stellenticket.de/de/rss/"
    OFFER_URL = "https://hu-berlin.stellenticket.de/de/offers/{offer_id}/"
    EMPLOYER_RE = re.compile(r"Arbeitgeber:\s*([^<\n]+)")
    LOCATION_RE = re.compile(r"Arbeitsort:\s*([^<\n]+)")
    OFFER_ID_RE = re.compile(r"/(\d+)/")

    def fetch(self) -> list[dict]:
        feed = feedparser.parse(self.FEED_URL)
        jobs = []
        for entry in feed.entries:
            content = ""
            if getattr(entry, "content", None):
                content = entry.content[0].get("value", "")
            company = self._fact(self.EMPLOYER_RE, content) or "HU Berlin"
            location = self._fact(self.LOCATION_RE, content)
            offer_id = self._offer_id(entry)

            title = html.unescape(entry.get("title", "")).strip()
            title = re.sub(rf"\s*\({re.escape(company)}\)\s*$", "", title)

            jobs.append({
                "title": title,
                "url": self.OFFER_URL.format(offer_id=offer_id) if offer_id else entry.get("link", ""),
                "description": content,
                "published": entry.get("updated", ""),
                "id": offer_id,
                "company": company,
                "location": location,
            })
        return jobs

    def _fact(self, pattern: re.Pattern, content: str) -> str:
        match = pattern.search(content)
        if not match:
            return ""
        return html.unescape(match.group(1)).strip()

    def _offer_id(self, entry) -> str:
        candidates = [entry.get("id", ""), entry.get("link", "")]
        for link in getattr(entry, "links", []):
            candidates.append(link.get("href", ""))
        for candidate in candidates:
            match = self.OFFER_ID_RE.search(candidate or "")
            if match:
                return match.group(1)
        return ""

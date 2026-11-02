from jobbot.interfaces import JobNormalizer
import hashlib
from datetime import datetime


class BhtNormalizer(JobNormalizer):
    """Normalize BHT Berlin RSS feed entries into the internal schema."""

    def normalize(self, raw_jobs: list[dict]) -> list[dict]:
        seen: set[str] = set()
        out: list[dict] = []
        for raw in raw_jobs:
            job = self.normalize_one(raw)
            key = self.dedupe_key(job)
            if key in seen or not job["title"]:
                continue
            seen.add(key)
            out.append(job)
        return out

    def normalize_one(self, raw: dict) -> dict:
        published = raw.get("published")
        posted = None
        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                posted = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                pass
        
        return {
            "external_id": raw.get("id", ""),
            "title": (raw.get("title") or "").strip(),
            "company": (raw.get("company") or "").strip(),
            "location": (raw.get("location") or "").strip(),
            "remote": False,
            "job_types": "",
            "tags": "",
            "url": raw.get("url") or "",
            "description": JobNormalizer.clean_html(raw.get("description") or ""),
            "posted": posted,
        }

    def dedupe_key(self, job: dict) -> str:
        basis = f"{job['title'].lower()}|{job['company'].lower()}"
        return hashlib.sha1(basis.encode()).hexdigest()

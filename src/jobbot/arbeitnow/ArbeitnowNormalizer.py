from jobbot.interfaces import JobNormalizer
from datetime import datetime


class ArbeitnowNormalizer(JobNormalizer):
    """Normalize Arbeitnow postings into the internal schema.
    # --------------------------------------------------------------------------
    #    NORMALIZE + DEDUPE — map every source onto one internal schema.
    #    Arbeitnow fields: slug, company_name, title, description (HTML-escaped),
    #    remote, url, tags, job_types, location, created_at (epoch seconds).
    # --------------------------------------------------------------------------
    """

    def normalize(self, raw_jobs: list[dict]) -> list[dict]:
        seen: set[str] = set()
        out: list[dict] = []
        for raw in raw_jobs:
            job = self.normalize_one(raw)
            key = JobNormalizer.dedupe_key(job)
            if key in seen or not job["title"]:
                continue
            seen.add(key)
            out.append(job)
        return out

    def normalize_one(self, raw: dict) -> dict:
        created_at = raw.get("created_at")
        posted = None
        if created_at is not None:
            posted = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M")
        return {
            "external_id": raw.get("slug") or raw.get("id"),
            "title": (raw.get("title") or "").strip(),
            "company": (raw.get("company_name") or "").strip(),
            "location": raw.get("location") or "",
            "remote": bool(raw.get("remote")),
            "job_types": ", ".join(raw.get("job_types") or []),
            "tags": ", ".join(raw.get("tags") or []),
            "url": raw.get("url") or "",
            "description": JobNormalizer.clean_html(raw.get("description") or ""),
            "posted": posted,
        }



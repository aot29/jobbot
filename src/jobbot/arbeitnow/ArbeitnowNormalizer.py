from jobbot.interfaces import JobNormalizer
import html
import re
import hashlib


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
            key = self.dedupe_key(job)
            if key in seen or not job["title"]:
                continue
            seen.add(key)
            out.append(job)
        return out

    def clean_html(self, text: str) -> str:
        """Unescape HTML entities and strip tags from a job description."""
        text = html.unescape(text or "")
        text = re.sub(r"<[^>]+>", " ", text)          # strip tags
        text = re.sub(r"\s+", " ", text).strip()       # collapse whitespace
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)  # remove control chars
        return text

    def normalize_one(self, raw: dict) -> dict:
        return {
            "external_id": raw.get("slug") or raw.get("id"),
            "title": (raw.get("title") or "").strip(),
            "company": (raw.get("company_name") or "").strip(),
            "location": raw.get("location") or "",
            "remote": bool(raw.get("remote")),
            "job_types": ", ".join(raw.get("job_types") or []),
            "tags": ", ".join(raw.get("tags") or []),
            "url": raw.get("url") or "",
            "description": self.clean_html(raw.get("description") or ""),
            "posted": raw.get("created_at"),  # epoch seconds or None
        }


    def dedupe_key(self, job: dict) -> str:
        basis = f"{job['title'].lower()}|{job['company'].lower()}"
        return hashlib.sha1(basis.encode()).hexdigest()

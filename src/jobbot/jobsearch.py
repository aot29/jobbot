"""
jobsearch.py — minimal job-search pipeline skeleton.

Flow:  fetch (aggregator APIs)  ->  normalize + dedupe  ->  keyword filter  ->  Excel export

Usage:
    pip install httpx pandas openpyxl
    python jobsearch.py

Then set up storage (SQLite) and scheduling (cron) as the next steps.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re

import httpx
import pandas as pd

# --------------------------------------------------------------------------
# 1. FETCHERS — one function per source, all return raw postings (dicts).
#    Start with Arbeitnow (free, no key). Add Adzuna / Greenhouse boards later.
# --------------------------------------------------------------------------

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow(pages: int = 2) -> list[dict]:
    jobs: list[dict] = []
    with httpx.Client(timeout=20) as client:
        for page in range(1, pages + 1):
            r = client.get(ARBEITNOW_URL, params={"page": page})
            r.raise_for_status()
            jobs.extend(r.json().get("data", []))
    return jobs


def fetch_all() -> list[dict]:
    """Add more fetchers here; each returns its own raw format."""
    return fetch_arbeitnow()


# --------------------------------------------------------------------------
# 2. NORMALIZE + DEDUPE — map every source onto one internal schema.
#    Arbeitnow fields: slug, company_name, title, description (HTML-escaped),
#    remote, url, tags, job_types, location, created_at (epoch seconds).
# --------------------------------------------------------------------------

import html


def clean_html(text: str) -> str:
    """Unescape HTML entities and strip tags from a job description."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)          # strip tags
    return re.sub(r"\s+", " ", text).strip()       # collapse whitespace


def normalize(raw: dict) -> dict:
    return {
        "external_id": raw.get("slug") or raw.get("id"),
        "title": (raw.get("title") or "").strip(),
        "company": (raw.get("company_name") or "").strip(),
        "location": raw.get("location") or "",
        "remote": bool(raw.get("remote")),
        "job_types": ", ".join(raw.get("job_types") or []),
        "tags": ", ".join(raw.get("tags") or []),
        "url": raw.get("url") or "",
        "description": clean_html(raw.get("description") or ""),
        "posted": raw.get("created_at"),  # epoch seconds or None
    }


def dedupe_key(job: dict) -> str:
    basis = f"{job['title'].lower()}|{job['company'].lower()}"
    return hashlib.sha1(basis.encode()).hexdigest()


def normalize_all(raw_jobs: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for raw in raw_jobs:
        job = normalize(raw)
        key = dedupe_key(job)
        if key in seen or not job["title"]:
            continue
        seen.add(key)
        out.append(job)
    return out


# --------------------------------------------------------------------------
# 3. FILTER — cheap keyword-based pre-filter (no LLM).
#    Excludes student/intern/PhD postings; flags research-flavored titles.
# --------------------------------------------------------------------------

BANNED = re.compile(
    r"(werkstudent|praktikant|praktikum|hiwi|studentische|studentische:r|"
    r"shk|doktorand|phd|dissertation|abschlussarbeit|trainee)",
    re.IGNORECASE,
)

RESEARCH_HINTS = re.compile(
    r"(research|forschung|wissenschaftlich|scientific|rse|eScience|"
    r"data engineer|hpc)",
    re.IGNORECASE,
)


def filter_jobs(jobs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for job in jobs:
        title = job["title"]
        if BANNED.search(title):
            continue
        job["is_research"] = bool(RESEARCH_HINTS.search(title))
        out.append(job)
    return out


# --------------------------------------------------------------------------
# 4. EXPORT — sorted spreadsheet for local use.
# --------------------------------------------------------------------------

COLUMNS = ["posted", "company", "title", "location", "is_research", "url"]


def export_excel(jobs: list[dict], path: str | None = None) -> str:
    path = path or f"jobs_{dt.date.today().isoformat()}.xlsx"
    df = pd.DataFrame(jobs)
    df = df[COLUMNS]

    # Research-flavored postings first, newest first within each group.
    df = df.sort_values(["is_research", "posted"], ascending=[False, False], na_position="last")
    df.to_excel(path, index=False, sheet_name="jobs")
    print(f"Wrote {len(df)} jobs to {path}")
    return path


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main() -> None:
    raw = fetch_all()
    jobs = normalize_all(raw)
    print(f"Fetched {len(raw)} raw, {len(jobs)} unique postings.")
    jobs = filter_jobs(jobs)
    print(f"{len(jobs)} postings after keyword filter.")
    export_excel(jobs)


if __name__ == "__main__":
    main()
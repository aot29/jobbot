from jobbot.interfaces import JobFetcher
import httpx


class ArbeitnowFetcher (JobFetcher):
    """Fetch jobs from Arbeitnow API (https://www.arbeitnow.com/api/job-board-api).
    # --------------------------------------------------------------------------
    #    FETCHERS — one function per source, all return raw postings (dicts).
    #    Start with Arbeitnow (free, no key). Add Adzuna / Greenhouse boards later.
    # --------------------------------------------------------------------------
    """

    def __init__(self, pages: int = 2):
        self.ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"
        self.pages = pages

    def fetch(self) -> list[dict]:
        jobs: list[dict] = []
        with httpx.Client(timeout=20) as client:
            for page in range(1, self.pages + 1):
                r = client.get(self.ARBEITNOW_URL, params={"page": page})
                r.raise_for_status()
                jobs.extend(r.json().get("data", []))
        return jobs

"""
jobsearch.py — minimal job-search pipeline skeleton.

Flow:  fetch (aggregator APIs)  ->  normalize + dedupe  ->  keyword filter  ->  Excel export

Usage:
    pip install httpx pandas openpyxl
    python jobsearch.py

Then set up storage (SQLite) and scheduling (cron) as the next steps.
"""

from __future__ import annotations

from jobbot.interfaces import *
from jobbot.arbeitnow.ArbeitnowNormalizer import ArbeitnowNormalizer
from jobbot.arbeitnow.ArbeitnowFetcher import ArbeitnowFetcher
from jobbot.filters.KeywordFilter import KeyWordFilter
from jobbot.serializers.Excel import Excel

class Pipeline:
    """Job-search pipeline: fetch -> normalize -> filter -> export."""

    def __init__(self,
                 fetcher: JobFetcher,
                 normalizer: JobNormalizer,
                 filter: JobFilter,
                 serializer: JobSerializer
                 ):
        self.fetcher = fetcher
        self.normalizer = normalizer
        self.filter = filter
        self.serializer = serializer

    def run(self) -> tuple[int, str]:
        raw = self.fetcher.fetch()
        jobs = self.normalizer.normalize(raw)
        jobs = self.filter.apply(jobs)
        num_entries, path = self.serializer.export(jobs)
        return num_entries, path

def main() -> None:
    fetcher = ArbeitnowFetcher(pages=10)
    normalizer = ArbeitnowNormalizer()
    filter = KeyWordFilter()
    serializer = Excel()
    pipeline = Pipeline(fetcher, normalizer, filter, serializer)
    num_entries, path = pipeline.run()
    print(f"Wrote {num_entries} jobs to {path}")


if __name__ == "__main__":
    main()
"""
jobsearch.py — minimal job-search pipeline skeleton.

Flow:  fetch (aggregator APIs)  ->  normalize + dedupe  ->  keyword filter  ->  Excel export

Usage:
    pip install httpx pandas openpyxl
    ./jobsearch.sh

Then set up storage (SQLite) and scheduling (cron) as the next steps.
"""

from __future__ import annotations
import os
import datetime as dt
from jobbot.interfaces import *
#from jobbot.arbeitnow.ArbeitnowNormalizer import ArbeitnowNormalizer
#from jobbot.arbeitnow.ArbeitnowFetcher import ArbeitnowFetcher
from jobbot.tuberlin.TuBerlinNormalizer import TuBerlinNormalizer
from jobbot.Pipeline import Pipeline
from jobbot.tuberlin.TuBerlinFetcher import TuBerlinFetcher
from jobbot.fuberlin.FuBerlinNormalizer import FuBerlinNormalizer
from jobbot.fuberlin.FuBerlinFetcher import FuBerlinFetcher
from jobbot.bht.BhtNormalizer import BhtNormalizer
from jobbot.bht.BhtFetcher import BhtFetcher
from jobbot.huberlin.HuBerlinNormalizer import HuBerlinNormalizer
from jobbot.huberlin.HuBerlinFetcher import HuBerlinFetcher
from jobbot.filters.KeywordFilter import KeyWordFilter
from jobbot.serializers.Excel import Excel


def main() -> None:

    filter = KeyWordFilter()
    serializer = Excel()

#    name = "Arbeitnow"
#    print(f"Processing {name}")
#    fetcher = ArbeitnowFetcher(pages=10)
#    normalizer = ArbeitnowNormalizer()
#    path = os.path.join("jobs", f"jobs_{name}_{dt.date.today().isoformat()}.xlsx")
#    ArbeitnowPipeline = Pipeline(path, fetcher, normalizer, filter, serializer)
#    num_entries = ArbeitnowPipeline.run()
#    print(f"{name} wrote {num_entries} jobs to {path}")

    name = "BHT"
    print(f"Processing {name}")
    fetcher = BhtFetcher()
    normalizer = BhtNormalizer()
    path = os.path.join("jobs", f"jobs_{name}_{dt.date.today().isoformat()}.xlsx")
    print(path)
    BHTpipeline = Pipeline(path, fetcher, normalizer, filter, serializer)
    num_entries = BHTpipeline.run()
    print(f"{name} wrote {num_entries} jobs to {path}")

    name = "TU"
    print(f"Processing {name}")
    fetcher = TuBerlinFetcher()
    normalizer = TuBerlinNormalizer()
    path = os.path.join("jobs", f"jobs_{name}_{dt.date.today().isoformat()}.xlsx")
    TUpipeline = Pipeline(path, fetcher, normalizer, filter, serializer)
    num_entries = TUpipeline.run()
    print(f"{name} wrote {num_entries} jobs to {path}")

    name = "FU"
    print(f"Processing {name}")
    fetcher = FuBerlinFetcher()
    normalizer = FuBerlinNormalizer()
    path = os.path.join("jobs", f"jobs_{name}_{dt.date.today().isoformat()}.xlsx")
    FUpipeline = Pipeline(path, fetcher, normalizer, filter, serializer)
    num_entries = FUpipeline.run()
    print(f"{name} wrote {num_entries} jobs to {path}")

    name = "HU"
    print(f"Processing {name}")
    fetcher = HuBerlinFetcher()
    normalizer = HuBerlinNormalizer()
    path = os.path.join("jobs", f"jobs_{name}_{dt.date.today().isoformat()}.xlsx")
    HUpipeline = Pipeline(path, fetcher, normalizer, filter, serializer)
    num_entries = HUpipeline.run()
    print(f"{name} wrote {num_entries} jobs to {path}")

if __name__ == "__main__":
    main()
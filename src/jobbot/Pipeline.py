from jobbot.interfaces import *

class Pipeline:
    """Job-search pipeline: fetch -> normalize -> filter -> export."""

    def __init__(self,
                 path: str,
                 fetcher: JobFetcher,
                 normalizer: JobNormalizer,
                 filter: JobFilter,
                 serializer: JobSerializer
                 ):
        self.path = path
        self.fetcher = fetcher
        self.normalizer = normalizer
        self.filter = filter
        self.serializer = serializer

    def run(self) -> tuple[int, str]:
        raw = self.fetcher.fetch()
        jobs = self.normalizer.normalize(raw)
        jobs = self.filter.apply(jobs)
        num_entries = self.serializer.export(self.path, jobs)
        return num_entries

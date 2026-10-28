from abc import ABC, abstractmethod


class JobNormalizer:
    """Abstract base class for job normalizers."""

    @abstractmethod
    def normalize(self, raw: list[dict]) -> list[dict]:
        """Normalize a raw posting into the internal schema."""
        raise NotImplementedError

class JobFetcher:
    """Abstract base class for job fetchers."""

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Fetch jobs from the source and return a list of raw postings."""
        raise NotImplementedError

class JobFilter:
    """Abstract base class for job filters."""

    @abstractmethod
    def apply(self, jobs: list[dict]) -> list[dict]:
        """Filter a list of normalized postings and return the filtered list."""
        raise NotImplementedError

class JobSerializer:
    """Abstract base class for job serializers."""

    @abstractmethod
    def export(self, jobs: list[dict], path: str | None = None) -> tuple[int, str]:
        """Serialize a list of normalized postings to a file and return the file path."""
        raise NotImplementedError
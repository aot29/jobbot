from abc import ABC, abstractmethod
import html
import re
import hashlib


class JobNormalizer:
    """Abstract base class for job normalizers."""

    @abstractmethod
    def normalize(self, raw: list[dict]) -> list[dict]:
        """Normalize a raw posting into the internal schema."""
        raise NotImplementedError

    @staticmethod
    def clean_html(text: str) -> str:
        """Unescape HTML entities and strip tags from a job description."""
        text = html.unescape(text or "")
        text = re.sub(r"<[^>]+>", " ", text)          # strip tags
        text = re.sub(r"\s+", " ", text).strip()       # collapse whitespace
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)  # remove control chars
        return text

    @staticmethod
    def dedupe_key(job: dict) -> str:
        basis = f"{job['title'].lower()}|{job['company'].lower()}"
        return hashlib.sha1(basis.encode()).hexdigest()

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
    def export(self, path: str, jobs: list[dict]) -> int:
        """Serialize a list of normalized postings to a file and return the file path."""
        raise NotImplementedError
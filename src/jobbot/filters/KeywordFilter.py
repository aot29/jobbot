import re
from jobbot.interfaces import JobFilter


class KeyWordFilter(JobFilter):
    """Filter job postings based on keywords in the title.
    # --------------------------------------------------------------------------
    # 3. FILTER — cheap keyword-based pre-filter (no LLM).
    #    Excludes student/intern/PhD postings; flags research-flavored titles.
    # --------------------------------------------------------------------------
    """

    def __init__(self):
      self.BANNED = re.compile(
          r"(werkstudent|praktikant|praktikum|hiwi|studentische|studentische:r|"
          r"shk|doktorand|phd|dissertation|abschlussarbeit|trainee)",
          re.IGNORECASE,
      )

      self.RESEARCH_HINTS = re.compile(
          r"(research|forschung|wissenschaftlich|scientific|rse|eScience|"
          r"data engineer|hpc)",
          re.IGNORECASE,
      )

    def apply(self, jobs: list[dict]) -> list[dict]:
        """Filter out unwanted jobs and flag research-flavored titles."""
        out: list[dict] = []
        for job in jobs:
            title = job["title"]
            if self.BANNED.search(title):
                continue
            job["is_research"] = bool(self.RESEARCH_HINTS.search(title))
            out.append(job)
        return out

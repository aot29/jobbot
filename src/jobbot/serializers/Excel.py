from jobbot.interfaces import JobSerializer
import hashlib
import pandas as pd

class Excel(JobSerializer):
    """Serialize a list of normalized postings to an Excel file.
    # --------------------------------------------------------------------------
    # EXPORT — sorted spreadsheet for local use.
    # --------------------------------------------------------------------------
    """

    def __init__(self):
        self.COLUMNS = ["id", "posted", "company", "title", "location", "is_research", "description", "url"]

    def export(self, path, jobs: list[dict]) -> int:
        print("exporting to Excel...")
        df = pd.DataFrame(jobs)

        # Stable id from URL
        df.insert(0, "id", df["url"].map(
            lambda u: hashlib.sha256(str(u).encode()).hexdigest()[:16]
        ))
        df = df[self.COLUMNS]

        # Research-flavored postings first, newest first within each group.
        df = df.sort_values(["is_research", "posted"], ascending=[False, False], na_position="last")
        df.to_excel(path, index=False, sheet_name="jobs")
        return len(df)

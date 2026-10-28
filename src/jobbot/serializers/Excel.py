from jobbot.interfaces import JobSerializer
import datetime as dt
import pandas as pd

class Excel(JobSerializer):
    """Serialize a list of normalized postings to an Excel file.
    # --------------------------------------------------------------------------
    # EXPORT — sorted spreadsheet for local use.
    # --------------------------------------------------------------------------
    """

    def __init__(self):
        self.COLUMNS = ["posted", "company", "title", "location", "is_research", "description", "url"]

    def export(self, jobs: list[dict], path: str | None = None) -> tuple[int, str]:
        print("exporting to Excel...")
        path = path or f"jobs_{dt.date.today().isoformat()}.xlsx"
        df = pd.DataFrame(jobs)
        df = df[self.COLUMNS]

        # Research-flavored postings first, newest first within each group.
        df = df.sort_values(["is_research", "posted"], ascending=[False, False], na_position="last")
        df.to_excel(path, index=False, sheet_name="jobs")
        return len(df),path

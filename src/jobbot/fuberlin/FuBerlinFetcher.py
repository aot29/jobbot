from jobbot.interfaces import JobFetcher
import feedparser
import html
import httpx
import re
import time


class FuBerlinFetcher(JobFetcher):
    """Fetch jobs from FU Berlin RSS feed.

    In this feed the <title> element holds the department/institute
    (Forschungsbereich) while the first line of <description> is the
    actual job title. The feed only carries a short teaser, so the
    full posting is scraped from the linked page. Two page layouts
    exist: the jobs.fu-berlin.de portal and the fu-berlin.de CMS.
    """

    FEED_URL = "https://www.fu-berlin.de/universitaet/beruf-karriere/jobs/wiss/gesamtliste/index.rss"
    PORTAL_DESCRIPTION_RE = re.compile(r'<span class="jobdescription">(.*?)</span>', re.S)
    CMS_JOB_BOX_RE = re.compile(r'<div class="box box-job-offer">(.*?)</main>', re.S)
    CMS_HEADER_RE = re.compile(r'<div class="box-job-offer-header">(.*?)</div>', re.S)
    CMS_CONTENT_RE = re.compile(r'<div class="editor-content[^"]*">(.*?)</div>', re.S)
    CMS_SPECIAL_RE = re.compile(r'<div class="box-job-offer-special-info">(.*?)</div>', re.S)

    def fetch(self) -> list[dict]:
        feed = feedparser.parse(self.FEED_URL)
        jobs = []
        with httpx.Client(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; jobbot)"},
        ) as client:
            for entry in feed.entries:
                department = entry.get("title", "")
                teaser = entry.get("description", "") or entry.get("summary", "")
                url = entry.get("link", "")

                title = self._teaser_title(teaser) or department
                description = self._full_description(client, url) or teaser
                if department:
                    description = f"{department}: {description}"

                jobs.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "published": entry.get("published", ""),
                    "id": entry.get("id", ""),
                })
                time.sleep(0.5)
        return jobs

    def _teaser_title(self, teaser: str) -> str:
        first_line = teaser.split("<br", 1)[0]
        return html.unescape(re.sub(r"<[^>]+>", " ", first_line)).strip()

    def _full_description(self, client: httpx.Client, url: str) -> str:
        if not url:
            return ""
        try:
            response = client.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            return ""
        match = self.PORTAL_DESCRIPTION_RE.search(response.text)
        if match:
            return self._to_text(match.group(1))
        return self._cms_description(response.text)

    def _cms_description(self, page: str) -> str:
        box = self.CMS_JOB_BOX_RE.search(page)
        if not box:
            return ""
        region = box.group(1)
        parts = []
        for pattern in (self.CMS_HEADER_RE, self.CMS_CONTENT_RE, self.CMS_SPECIAL_RE):
            match = pattern.search(region)
            if match:
                text = self._to_text(match.group(1))
                if text:
                    parts.append(text)
        return "\n\n".join(parts) if parts else ""

    def _to_text(self, html_text: str) -> str:
        text = re.sub(r"(?i)<(br|/p|/li|/h[1-6]|/div)[^>]*>", "\n", html_text)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        text = text.replace("\r", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

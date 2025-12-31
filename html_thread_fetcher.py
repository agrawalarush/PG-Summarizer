import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from typing import List
import config

class HTMLThreadFetcher:
    def __init__(self):
        self.base_url = config.PG_HACKERS_ARCHIVE_BASE
        self.max_threads = getattr(config, "MAX_THREADS", None)

    def get_today_thread_urls(self) -> List[str]:
        """Fetch today's thread URLs (flat view), respecting MAX_THREADS_PER_DAY."""
        today_plus_one = datetime.now() + timedelta(days=1)
        today_str = today_plus_one.strftime("%Y%m%d0000")

        daily_page_url = urljoin(self.base_url, f"since/{today_str}/")
        visited = set()
        urls = []

        try:
            resp = requests.get(daily_page_url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            for a in soup.find_all("a", href=True):
                if self.max_threads is not None and len(urls) >= self.max_threads:
                    break

                href = a["href"]
                if "/message-id/" not in href:
                    continue

                # convert to flat view
                if "/flat/" not in href:
                    mid = href.split("/message-id/")[1].split("#")[0]
                    href = f"/message-id/flat/{mid}"

                thread_url = href if href.startswith("http") else urljoin(self.base_url, href)

                if thread_url not in visited:
                    visited.add(thread_url)
                    urls.append(thread_url)

        except Exception as e:
            print(f"Error fetching {daily_page_url}: {e}")

        return urls

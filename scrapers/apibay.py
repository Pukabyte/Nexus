import time
import aiohttp

from utils.logger import logger
from scrapers import BaseScraper


class Apibay(BaseScraper):
    """`Apibay` scraper class"""

    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session is open"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session if it's open"""
        if self.session:
            await self.session.close()

    async def search(self, query, page, limit):
        """Search torrents from `Apibay`."""
        await self._ensure_session()
        start_time = time.time()
        url = f"{self.url}/q.php?q={query}"
        data = {"data": [], "total": 0}
        counter = 0
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    json_response = await response.json()
                    if json_response and isinstance(json_response, list):
                        for item in json_response:
                            if counter == limit:
                                break
                            if isinstance(item, dict):
                                data["data"].append({
                                    "name": item.get("name", "N/A"),
                                    "infohash": item.get("info_hash", "N/A"),
                                    "site": self.url
                                })
                                counter += 1
                        data["total"] = len(data["data"])
        except Exception as e:
            logger.error(f"Exception during search: {e}")
        finally:
            await self.close()

        data["time"] = time.time() - start_time
        return data

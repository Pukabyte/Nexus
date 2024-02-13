import time
import aiohttp

from utils.logger import logger
from scrapers import BaseScraper


class Apibay(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit
        self.session = None

    async def _ensure_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def search(self, query, page, limit):
        await self._ensure_session()  # Ensure session is ready
        start_time = time.time()
        url = f"{self.url}/q.php?q={query}&cat=201"
        data = {"data": [], "total": 0}

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    json_response = await response.json()
                    if json_response and isinstance(json_response, list):  # Assuming the expected response is a list
                        for item in json_response:
                            if isinstance(item, dict):  # Ensure each item is a dictionary
                                data["data"].append({
                                    "name": item.get("name", "N/A"),  # Provide default values
                                    "info_hash": item.get("info_hash", "N/A"),
                                    "category": item.get("category", "N/A"),
                                    "details": item.get("details", "N/A"),
                                    "download": item.get("download", "N/A"),
                                    "seeders": item.get("seeders", 0),
                                    "leechers": item.get("leechers", 0),
                                    "size": item.get("size", "N/A")
                                })
                        data["total"] = len(data["data"])
        except Exception as e:
            logger.error(f"Exception during search: {e}")

        data["time"] = time.time() - start_time
        return data

    async def parser_result(self, start_time, url, session):
        html = await self.get_all_results(session, url)
        results = self._parser(html)
        if results is not None:
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return results

    async def recent(self):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            url = self.url + "/precompiled/data_top100_recent.json"
            return await self.parser_result(start_time, url, session)

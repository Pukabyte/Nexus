import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import HEADER_AIO, BaseScraper, asyncio_fix
from utils.logger import logger


class Kickass(BaseScraper):
    """`Kickass` scraper class"""

    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        """Scrap individual torrent page for name, infohash"""
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                mag = soup.find_all("a", class_="kaGiantButton")
                magnet = mag[0]["href"]
                hash = re.search(r"btih:([a-fA-F\d]{40})", magnet).group(1)
                if hash:
                    obj["infohash"] = hash
                    obj["site"] = self.url
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    async def _get_torrent(self, result, session, urls):
        """Get the torrent from individual torrent page"""
        tasks = []
        for idx, url in enumerate(urls):
            task = asyncio.create_task(
                self._individual_scrap(session, url, result["data"][idx])
            )
            tasks.append(task)
        await asyncio.gather(*tasks)
        return result

    def _parser(self, htmls):
        """Parse the result from the given HTML."""
        try:
            my_dict = {"data": []}
            list_of_urls = []
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                for tr in soup.select("tr.odd,tr.even"):
                    name = tr.find("a", class_="cellMainLink").text.strip()
                    url = self.url + tr.find("a", class_="cellMainLink")["href"]
                    list_of_urls.append(url)
                    if name:
                        my_dict["data"].append({"name": name})
                    if len(my_dict["data"]) == self.limit:
                        break
            return my_dict, list_of_urls
        except Exception as e:
            logger.error(f"Error: {e}")
            return None, None

    async def parser_result(self, url, session):
        """Parse the result from the given URL."""
        start_time = time.time()
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            results["data"] = [
                {
                    "name": item["name"],
                    "infohash": item.get("infohash"),
                    "site": item.get("site"),
                }
                for item in results["data"]
            ]
            return results
        return result

    def _build_url(self, category, path):
        """Build the URL based on the category and path."""
        if category:
            if category == "tv":
                category = "television"
            elif category == "apps":
                category = "applications"
            return f"{self.url}/{path}-{category}/"
        return f"{self.url}/{path}/"

    async def search(self, query, page, limit):
        """Search torrents from `Kickass`."""
        async with aiohttp.ClientSession() as session:
            self.limit = limit
            url = f"{self.url}/usearch/{query}/{page}/"
            return await self.parser_result(url, session)

    async def trending(self, category, page, limit):
        """Get trending torrents from `Kickass`."""
        async with aiohttp.ClientSession() as session:
            self.limit = limit
            url = self._build_url(category, "top-100")
            return await self.parser_result(url, session)

    async def recent(self, category, page, limit):
        """Get recent torrents from `Kickass`."""
        async with aiohttp.ClientSession() as session:
            self.limit = limit
            url = self._build_url(category, "new")
            return await self.parser_result(url, session)

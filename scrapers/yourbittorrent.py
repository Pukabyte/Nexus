import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import HEADER_AIO, BaseScraper, asyncio_fix


class YourBittorrent(BaseScraper):
    """`YourBittorrent` scraper class"""

    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        """Scrap individual torrent page for infohash"""
        async with session.get(url, headers=HEADER_AIO) as res:
            html = await res.text(encoding="ISO-8859-1")
            soup = BeautifulSoup(html, "html.parser")
            try:
                hash_selector = "body > div > div:nth-child(4) > div.card-body.container > div > div.col > div:nth-child(10) > div.col > kbd"
                infohash = soup.select_one(hash_selector).text
                if infohash:
                    obj["infohash"] = infohash
                    obj["site"] = self.url
                    obj.pop("url")
                else:
                    return None
            except:
                return None

    async def _get_torrent(self, result, session, urls):
        """Get the torrent from individual torrent page"""
        tasks = []
        for idx, url in enumerate(urls):
            tasks.append(
                asyncio.create_task(
                    self._individual_scrap(session, url, result["data"][idx])
                )
            )
        await asyncio.gather(*tasks)
        result["data"] = [
            torrent for torrent in result["data"] if "infohash" in torrent
        ]
        return result

    def _parser(self, htmls, idx=1):
        """Parse the result from the given HTML."""
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}

                for tr in soup.find_all("tr")[idx:]:
                    td = tr.find_all("td")
                    name = td[1].find("a").get_text(strip=True)
                    url = self.url + td[1].find("a")["href"]
                    list_of_urls.append(url)
                    my_dict["data"].append(
                        {
                            "name": name,
                            "url": url,
                        }
                    )
                    if len(my_dict["data"]) == self.limit:
                        break
                return my_dict, list_of_urls
        except:
            return None, None

    async def parser_result(self, start_time, url, session, idx=1):
        """Parse the result from the given URL."""
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls, idx)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return result

    async def search(self, query, page, limit):
        """Search the given query from the website"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/?v=&c=&q={}".format(query)
            return await self.parser_result(start_time, url, session, idx=6)

    async def trending(self, category, page, limit):
        """Get the trending torrents from the website"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            idx = None
            if not category:
                url = self.url + "/top.html"
                idx = 1
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + f"/{category}.html"
                idx = 4
            return await self.parser_result(start_time, url, session, idx)

    async def recent(self, category, page, limit):
        """Get the recent torrents from the website"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            idx = None
            if not category:
                url = self.url + "/new.html"
                idx = 1
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + f"/{category}/latest.html"
                idx = 4
            return await self.parser_result(start_time, url, session, idx)

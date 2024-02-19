import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import HEADER_AIO, BaseScraper, asyncio_fix


class Yts(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url):
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                name = soup.select_one("div.hidden-xs h1").text
                torrents = []
                for div in soup.find_all("div", class_="modal-torrent"):
                    quality = div.find("div", class_="modal-quality").find("span").text
                    magnet = div.find("a", class_="magnet-download")["href"]
                    infohash = re.search(r"btih:([a-fA-F0-9]{40})", magnet).group(1)
                    torrents.append({"quality": quality, "infohash": infohash})
                return {"name": name, "torrents": torrents, "site": self.url}
        except Exception:
            return None

    async def _get_torrent(self, result, session, urls):
        tasks = [self._individual_scrap(session, url) for url in urls]
        movies_data = await asyncio.gather(*tasks)
        flat_results = []
        for movie in movies_data:
            if not movie:
                continue
            for torrent in movie["torrents"]:
                name_with_quality = f"{movie['name']} [{torrent['quality']}]"
                flat_results.append(
                    {
                        "name": name_with_quality,
                        "infohash": torrent["infohash"],
                        "site": movie["site"],
                    }
                )
        result["data"] = flat_results
        return result

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}
                for div in soup.find_all("div", class_="browse-movie-wrap"):
                    url = div.find("a")["href"]
                    list_of_urls.append(url)
                    my_dict["data"].append({"url": url})
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    ul = soup.find("ul", class_="tsc_pagination")
                    current_page = ul.find("a", class_="current").text
                    my_dict["current_page"] = int(current_page)
                    if current_page:
                        total_results = soup.select_one(
                            "body > div.main-content > div.browse-content > div > h2 > b"
                        ).text
                        if "," in total_results:
                            total_results = total_results.replace(",", "")
                        total_page = int(total_results) / 20
                        my_dict["total_pages"] = (
                            int(total_page) + 1
                            if type(total_page) == float
                            else int(total_page)
                        )

                except:
                    ...
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if page != 1:
                url = (
                    self.url
                    + "/browse-movies/{}/all/all/0/latest/0/all?page={}".format(
                        query, page
                    )
                )
            else:
                url = self.url + "/browse-movies/{}/all/all/0/latest/0/all".format(
                    query
                )
            return await self.parser_result(start_time, url, session)

    async def parser_result(self, start_time, url, session):
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return result

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/trending-movies"
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if page != 1:
                url = (
                    self.url
                    + "/browse-movies/0/all/all/0/featured/0/all?page={}".format(page)
                )
            else:
                url = self.url + "/browse-movies/0/all/all/0/featured/0/all"
            return await self.parser_result(start_time, url, session)

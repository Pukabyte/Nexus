import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import BaseScraper


class TorrentGalaxy(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    def _parser_individual(self, html):
        try:
            soup = BeautifulSoup(html[0], "html.parser")
            my_dict = {"data": []}
            root = soup.find("div", class_="gluewrapper").select(
                "div > :nth-child(2) > div > .tprow"
            )

            name = root[0].find_all("div")[-1].get_text(strip=True)
            category = root[3].find_all("div")[-1].get_text(strip=True).split(">")[0]
            if category != "XXX":
                return None
            infohash = root[6].find_all("div")[-1].get_text(strip=True)
            soup.find("div", id="intblockslide").find_all("a")
            my_dict["data"].append(
                {"name": name, "infohash": infohash, "site": self.url}
            )
            return my_dict
        except:
            return None

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                my_dict = {"data": []}
                for _, divs in enumerate(soup.find_all("div", class_="tgxtablerow")):
                    div = divs.find_all("div")
                    try:
                        name = div[4].find("a").get_text(strip=True)
                    except:
                        name = (div[1].find("a", class_="txlight")).find("b").text
                    if name != "":
                        try:
                            magnet = div[5].find_all("a")[1]["href"]
                        except:
                            magnet = div[3].find_all("a")[1]["href"]
                        category = (
                            (div[0].find("small").text.replace("&nbsp", ""))
                            .split(":")[0]
                            .strip()
                        )
                        if category not in ["XXX", "Books", "Games"]:
                            my_dict["data"].append(
                                {
                                    "name": name,
                                    "infohash": re.search(
                                        r"([{a-f\d,A-F\d}]{40})\b", magnet
                                    ).group(0),
                                    "site": self.url,
                                }
                            )
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    ul = soup.find_all("ul", class_="pagination")[-1]
                    tpages = ul.find_all("li")[-2]
                    my_dict["current_page"] = int(
                        soup.select_one("li.page-item.active.txlight a").text.split(
                            " "
                        )[0]
                    )
                    my_dict["total_pages"] = int(tpages.find("a").text)
                except:
                    ...
                return my_dict
        except:
            return None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = (
                self.url
                + "/torrents.php?search=+{}&sort=seeders&order=desc&page={}".format(
                    query, page - 1
                )
            )
            return await self.parser_result(start_time, url, session)

    async def get_torrent_by_url(self, torrent_url):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            return await self.parser_result(
                start_time, torrent_url, session, is_individual=True
            )

    async def parser_result(self, start_time, url, session, is_individual=False):
        html = await self.get_all_results(session, url)
        if is_individual:
            results = self._parser_individual(html)
        else:
            results = self._parser(html)
        if results is not None:
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return results

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/latest"
            else:
                if category == "documentaries":
                    category = "Docus"
                url = (
                    self.url
                    + "/torrents.php?parent_cat={}&sort=id&order=desc&page={}".format(
                        str(category).capitalize(), page - 1
                    )
                )
            return await self.parser_result(start_time, url, session)

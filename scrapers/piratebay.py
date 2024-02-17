import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper


class PirateBay(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")

                my_dict = {"data": []}
                for tr in soup.find_all("tr")[1:]:
                    td = tr.find_all("td")
                    try:
                        name = td[1].find("div").find("a").text
                    except:
                        name = None
                    if name:
                        category = td[0].find_all("a")[0].text
                        if category != "Video":
                            continue
                        magnet = td[1].find_all("a")[1]["href"]
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
                return my_dict
        except:
            return None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/search/{}/{}/99/0".format(query, page)
            return await self.parser_result(start_time, url, session)

    async def parser_result(self, start_time, url, session):
        html = await self.get_all_results(session, url)
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
            url = self.url + "/top/all"
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/recent"
            else:
                url = self.url + "/{}/latest/".format(category)
            return await self.parser_result(start_time, url, session)

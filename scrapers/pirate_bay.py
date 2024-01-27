import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper
from utils.sites import sites


class PirateBay(BaseScraper):
    def __init__(self):
        self.url = sites.pirate_bay.website
        self.limit = None

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
                        url = td[1].find("div").find("a")["href"]
                        magnet = td[1].find_all("a")[1]["href"]
                        seeders = td[2].text
                        leechers = td[3].text
                        mixed = td[1].find_all("font")[0].text
                        mixed = re.sub(r"(Uploaded|Size|ULed by)", "", mixed).split(",")
                        category = td[0].find_all("a")[0].text
                        my_dict["data"].append(
                            {
                                "name": name,
                                "size": mixed[1].strip(),
                                "seeders": seeders,
                                "leechers": leechers,
                                "category": category,
                                "uploader": mixed[-1].strip(),
                                "url": url,
                                "date": mixed[0].strip(),
                                "hash": re.search(
                                    r"([{a-f\d,A-F\d}]{32,40})\b", magnet
                                ).group(0),
                                "magnet": magnet,
                            }
                        )
                    if len(my_dict["data"]) == self.limit:
                        break
                last_tr = soup.find_all("tr")[-1]
                check_if_pagination_available = last_tr.find("td").find("center")
                if not check_if_pagination_available:
                    current_page = last_tr.find("td").find("b").text
                    my_dict["current_page"] = int(current_page)
                    my_dict["total_pages"] = int(
                        last_tr.find("td").find_all("a")[-2].text
                    )
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

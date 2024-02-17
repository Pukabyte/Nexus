import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper


class Glodls(BaseScraper):
    """`Glodls` scraper class"""

    def __init__(self, website, limit):
        self.url = website
        self.limit = limit

    def _parser(self, htmls):
        """Parse the result from the given HTML."""
        try:
            counter = 0
            for html in htmls:
                if counter == self.limit:
                    break
                soup = BeautifulSoup(html, "html.parser")
                my_dict = {"data": []}
                for tr in soup.find_all("tr", class_="t-row")[0:-1:2]:
                    td = tr.find_all("td")
                    name = td[1].find_all("a")[-1].find("b").text
                    magnet = td[3].find("a")["href"]
                    infohash = re.search(r"btih:(.{40})", magnet).group(1)
                    my_dict["data"].append(
                        {"name": name, "infohash": infohash, "site": self.url}
                    )
                    counter += 1
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    pagination = soup.find("div", class_="pagination")
                    total_pages = pagination.find_all("a")[-2]["href"]
                    total_pages = total_pages.split("=")[-1]
                    my_dict["total_pages"] = int(total_pages) + 1
                except:
                    pass
                return my_dict
        except:
            return None

    async def search(self, query, page, limit):
        """Search torrents from `Glodls`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = (
                self.url
                + "/search_results.php?search={}&cat=0&incldead=0&inclexternal=0&lang=0&sort=seeders&order=desc&page={}".format(
                    query, page - 1
                )
            )
            return await self.parser_result(start_time, url, session)

    async def parser_result(self, start_time, url, session):
        """Parse the result from the given URL."""
        html = await self.get_all_results(session, url)
        results = self._parser(html)
        if results is not None:
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return results

    async def trending(self, category, page, limit):
        """Get trending torrents from `Glodls`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/today.php"
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        """Get recent torrents from `Glodls`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/search.php"
            return await self.parser_result(start_time, url, session)

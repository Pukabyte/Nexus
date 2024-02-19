import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper


class BitSearch(BaseScraper):
    """`BitSearch` scraper class"""

    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    def _parser(self, htmls):
        """Parse the result from the given HTML."""
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")

                my_dict = {"data": []}
                for divs in soup.find_all("li", class_="search-result"):
                    if len(my_dict["data"]) == self.limit:
                        break
                    info = divs.find("div", class_="info")
                    name = info.find("h5", class_="title").find("a").text
                    category = info.find("div").find("a", class_="category").text
                    if not category:
                        continue
                    stats = info.find("div", class_="stats").find_all("div")
                    if stats:
                        links = divs.find("div", class_="links").find_all("a")
                        magnet = links[1]["href"]
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
                    total_pages = (
                        int(
                            soup.select(
                                "body > main > div.container.mt-2 > div > div:nth-child(1) > div > span > b"
                            )[0].text
                        )
                        / 20
                    )  # !20 search result available on each page
                    total_pages = (
                        total_pages + 1
                        if type(total_pages) == float
                        else total_pages
                        if int(total_pages) > 0
                        else total_pages + 1
                    )

                    current_page = int(
                        soup.find("div", class_="pagination")
                        .find("a", class_="active")
                        .text
                    )
                    my_dict["current_page"] = current_page
                    my_dict["total_pages"] = int(total_pages)
                except:
                    ...
                return my_dict
        except:
            return None

    async def search(self, query, page, limit):
        """Search torrents from `BitSearch`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/search?q={}&page={}".format(query, page)
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
        """Show trending torrents from `BitSearch`."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/trending"
            return await self.parser_result(start_time, url, session)

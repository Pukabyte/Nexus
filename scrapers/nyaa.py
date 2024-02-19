import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import BaseScraper


class NyaaSi(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")

                my_dict = {"data": []}
                for tr in (soup.find("table")).find_all("tr")[1:]:
                    td = tr.find_all("td")
                    name = td[1].find_all("a")[-1].text
                    magnet_and_torrent = td[2].find_all("a")
                    magnet = magnet_and_torrent[-1]["href"]
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
                    ul = soup.find("ul", class_="pagination")
                    tpages = ul.find_all("a")[-2].text
                    current_page = (ul.find("li", class_="active")).find("a").text
                    my_dict["current_page"] = int(current_page)
                    my_dict["total_pages"] = int(tpages)
                except:
                    my_dict["current_page"] = None
                    my_dict["total_pages"] = None
                return my_dict
        except:
            return None

    async def parser_result(self, start_time, url, session, retry_count=0):
        try:
            html = await self.get_all_results(session, url)
            results = self._parser(html)
            if results is not None:
                results["time"] = time.time() - start_time
                results["total"] = len(results["data"])
                return results
            return results
        except aiohttp.ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                if retry_count < 2:  # Maximum retries
                    retry_count += 1
                    await asyncio.sleep(2**retry_count)  # Exponential backoff
                    return await self.parser_result(
                        start_time, url, session, retry_count
                    )
                else:
                    print("Reached maximum retries. Skipping scraping.")
                    return None
            else:
                print("Unexpected error occurred:", e)
                return None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/?f=0&c=0_0&q={}".format(query)
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url
            return await self.parser_result(start_time, url, session)

import asyncio
import re
import time

import aiohttp
from bs4 import BeautifulSoup

from scrapers import HEADER_AIO, BaseScraper, asyncio_fix


class X1337(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                try:
                    magnet = soup.select_one(".no-top-radius > div > ul > li > a")[
                        "href"
                    ]
                    if magnet:
                        obj["infohash"] = re.search(
                            r"([{a-f\d,A-F\d}]{40})\b", magnet
                        ).group(0)
                        obj["site"] = self.url
                        obj.pop("url")
                except IndexError:
                    ...
        except:
            return None

    async def _get_torrent(self, result, session, urls):
        tasks = []
        for idx, url in enumerate(urls):
            for obj in result["data"]:
                if obj["url"] == url:
                    task = asyncio.create_task(
                        self._individual_scrap(session, url, result["data"][idx])
                    )
                    tasks.append(task)
        await asyncio.gather(*tasks)
        return result

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}
                trs = soup.select("tbody tr")
                for tr in trs:
                    td = tr.find_all("td")
                    name = td[0].find_all("a")[-1].text
                    if name:
                        url = self.url + td[0].find_all("a")[-1]["href"]
                        list_of_urls.append(url)
                        my_dict["data"].append(
                            {
                                "name": name,
                                "url": url,
                            }
                        )
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    pages = soup.select(".pagination li a")
                    my_dict["current_page"] = int(pages[0].text)
                    tpages = pages[-1].text
                    if tpages == ">>":
                        my_dict["total_pages"] = int(pages[-2].text)
                    else:
                        my_dict["total_pages"] = int(pages[-1].text)
                except:
                    ...
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            self.limit = limit
            start_time = time.time()
            url = self.url + "/search/{}/{}/".format(query, page)
            return await self.parser_result(
                start_time, url, session, query=query, page=page
            )

    async def parser_result(self, start_time, url, session, page, query=None):
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            if query is None:
                return results
            while True:
                if len(results["data"]) >= self.limit:
                    results["data"] = results["data"][0 : self.limit]
                    results["total"] = len(results["data"])
                    return results
                page = page + 1
                url = self.url + "/search/{}/{}/".format(query, page)
                htmls = await self.get_all_results(session, url)
                result, urls = self._parser(htmls)
                if result is not None:
                    if len(result["data"]) > 0:
                        res = await self._get_torrent(result, session, urls)
                        for obj in res["data"]:
                            results["data"].append(obj)
                        try:
                            results["current_page"] = res["current_page"]
                        except:
                            ...
                        results["total"] = len(results["data"])
                        results["time"] = time.time() - start_time
                    else:
                        break
                else:
                    break
            return results
        return result

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/home/"
            else:
                url = self.url + "/popular-{}".format(category.lower())
            return await self.parser_result(start_time, url, session, page)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/trending"
            else:
                url = self.url + "/cat/{}/{}/".format(str(category).capitalize(), page)
            return await self.parser_result(start_time, url, session, page)

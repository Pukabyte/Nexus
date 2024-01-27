import asyncio
import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, decorator_asyncio_fix
from utils.sites import sites


class Kickass(BaseScraper):
    def __init__(self):
        self.url = sites.kickass.website
        self.limit = None

    @decorator_asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                try:
                    poster = soup.find("a", class_="movieCover")
                    if poster:
                        poster = poster.find("img")["src"]
                        obj["poster"] = self.url + poster
                    imgs = (soup.find("div", class_="data")).find_all("img")
                    if imgs and len(imgs) > 0:
                        obj["screenshot"] = [img["src"] for img in imgs]
                    magnet_and_torrent = soup.find_all("a", class_="kaGiantButton")
                    magnet = magnet_and_torrent[0]["href"]
                    obj["hash"] = re.search(
                        r"([{a-f\d,A-F\d}]{32,40})\b", magnet
                    ).group(0)
                    obj["magnet"] = magnet
                except:
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
                for tr in soup.select("tr.odd,tr.even"):
                    td = tr.find_all("td")
                    name = tr.find("a", class_="cellMainLink").text.strip()
                    url = self.url + tr.find("a", class_="cellMainLink")["href"]
                    list_of_urls.append(url)
                    if name:
                        size = td[1].text.strip()
                        seeders = td[4].text.strip()
                        leechers = td[5].text.strip()
                        uploader = td[2].text.strip()
                        date = td[3].text.strip()

                        my_dict["data"].append(
                            {
                                "name": name,
                                "size": size,
                                "date": date,
                                "seeders": seeders,
                                "leechers": leechers,
                                "url": url,
                                "uploader": uploader,
                            }
                        )
                    if len(my_dict["data"]) == self.limit:
                        break
                try:
                    pages = soup.find("div", class_="pages")
                    current_page = int(pages.find("a", class_="active").text)
                    pages = pages.find_all("a")
                    total_page = pages[-1].text
                    if total_page == ">>":
                        total_page = pages[-2].text
                    my_dict["current_page"] = current_page
                    my_dict["total_pages"] = int(total_page)
                except:
                    ...
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/usearch/{}/{}/".format(query, page)
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
            if not category:
                url = self.url + "/top-100"
            else:
                if category == "tv":
                    category == "television"
                elif category == "apps":
                    category = "applications"
                url = self.url + "/top-100-{}/".format(category)
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/new/"
            else:
                url = self.url + "/{}/".format(category)
            return await self.parser_result(start_time, url, session)

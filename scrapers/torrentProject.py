import asyncio
import time
import aiohttp
import requests
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, decorator_asyncio_fix
from utils.sites import sites


class TorrentProject(BaseScraper):
    def __init__(self):
        self.url = sites.torrentproject.website
        self.limit = None

    @decorator_asyncio_fix
    async def _individual_scrap(self, session, url, obj, sem):
        async with sem:
            try:
                async with session.get(
                    url,
                    headers=HEADER_AIO,
                ) as res:
                    html = await res.text(encoding="ISO-8859-1")
                    soup = BeautifulSoup(html, "html.parser")
                    try:
                        magnet = soup.select_one(
                            "#download > div:nth-child(2) > div > a"
                        )["href"]
                        index_of_magnet = magnet.index("magnet")
                        magnet = requests.utils.unquote(magnet[index_of_magnet:])
                        obj["magnet"] = magnet
                    except:
                        ...
            except:
                return None

    async def _get_torrent(self, result, session, urls):
        tasks = []
        sem = asyncio.Semaphore(3)
        for idx, url in enumerate(urls):
            for obj in result["data"]:
                if obj["url"] == url:
                    task = asyncio.create_task(
                        self._individual_scrap(session, url, result["data"][idx], sem)
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
                for div in soup.select("div#similarfiles div")[2:]:
                    span = div.find_all("span")
                    name = span[0].find("a").text
                    url = self.url + span[0].find("a")["href"]
                    list_of_urls.append(url)
                    seeders = span[2].text
                    leechers = span[3].text
                    date = span[4].text
                    size = span[5].text

                    my_dict["data"].append(
                        {
                            "name": name,
                            "size": size,
                            "date": date,
                            "seeders": seeders,
                            "leechers": leechers,
                            "url": url,
                        }
                    )
                    if len(my_dict["data"]) == self.limit:
                        break
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/?t={}&p={}".format(query, page - 1)
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

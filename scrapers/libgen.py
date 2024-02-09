import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, asyncio_fix
from utils.logger import logger


class Libgen(BaseScraper):
    def __init__(self, website, limit):
        super().__init__()
        self.url = website
        self.limit = limit

    @asyncio_fix
    async def _individual_scrap(self, session, url, obj, sem):
        async with sem:
            try:
                async with session.get(url, headers=HEADER_AIO) as res:
                    html = await res.text(encoding="ISO-8859-1")
                    soup = BeautifulSoup(html, "html.parser")
                    try:
                        x = soup.find_all("a")
                        for a in x:
                            if a.text == "One-filetorrent":
                                if a["href"] != "#":
                                    obj["torrent"] = self.url + a["href"]
                        poster = soup.find_all("img")[0]

                        if poster:
                            obj["poster"] = "http://library.lol" + poster["src"]
                    except Exception as e:
                        logger.exception("Error in libgen: {}".format(e))
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
                trs = soup.select("[valign=top]")
                for tr in trs[1:]:
                    td = tr.find_all("td")
                    id = td[0].text
                    authors = []
                    author = td[1].find_all("a")
                    for a in author:
                        authors.append(a.text.strip())
                    name_and_url = td[2].find("a")
                    name = name_and_url.text
                    url = self.url + "/" + name_and_url["href"]
                    list_of_urls.append(url)
                    publisher = td[3].text
                    year = td[4].text
                    pages = None
                    try:
                        pages = td[5].text
                    except:
                        ...
                    language = td[6].text
                    size = td[7].text
                    extension = td[8].text

                    my_dict["data"].append(
                        {
                            "id": id,
                            "authors": authors,
                            "name": name,
                            "publisher": publisher,
                            "year": year,
                            "pages": pages,
                            "language": language,
                            "size": size,
                            "extension": extension,
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
            url = (
                self.url
                + "/search.php?req={}&lg_topic=libgen&open=0&view=simple&res=100&phrase=1&column=def".format(
                    query
                )
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

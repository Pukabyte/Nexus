import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, asyncio_fix


class YourBittorrent(BaseScraper):
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
                    container = soup.select_one("div.card-body.container")
                    poster = (
                        container.find("div")
                        .find_all("div")[0]
                        .find("picture")
                        .find("img")["src"]
                    )
                    clearfix = soup.find("div", class_="clearfix")
                    torrent = clearfix.find("div").find_all("div")[1].find("a")["href"]
                    obj["torrent"] = torrent
                    obj["poster"] = poster
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

    def _parser(self, htmls, idx=1):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}

                for tr in soup.find_all("tr")[idx:]:
                    td = tr.find_all("td")
                    name = td[1].find("a").get_text(strip=True)
                    url = self.url + td[1].find("a")["href"]
                    list_of_urls.append(url)
                    size = td[2].text
                    date = td[3].text
                    seeders = td[4].text
                    leechers = td[5].text
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
            url = self.url + "/?v=&c=&q={}".format(query)
            return await self.parser_result(start_time, url, session, idx=6)

    async def parser_result(self, start_time, url, session, idx=1):
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls, idx)
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
            idx = None
            if not category:
                url = self.url + "/top.html"
                idx = 1
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + f"/{category}.html"
                idx = 4
            return await self.parser_result(start_time, url, session, idx)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            idx = None
            if not category:
                url = self.url + "/new.html"
                idx = 1
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + f"/{category}/latest.html"
                idx = 4
            return await self.parser_result(start_time, url, session, idx)

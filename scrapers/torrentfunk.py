import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, asyncio_fix


class TorrentFunk(BaseScraper):
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
                    obj["torrent"] = soup.select_one(
                        "#right > main > div.content > table:nth-child(3) > tr > td:nth-child(2) > a"
                    )["href"]
                    obj["category"] = soup.select_one(
                        "#right > main > div.content > table:nth-child(7) > tr> td:nth-child(2) > a"
                    ).text
                    obj["hash"] = soup.select_one(
                        "#right > main > div.content > table:nth-child(7) > tr:nth-child(3) > td:nth-child(2)"
                    ).text
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

                for tr in soup.select(".tmain tr")[idx:]:
                    td = tr.find_all("td")
                    if len(td) == 0:
                        continue
                    name = td[0].find("a").text
                    date = td[1].text
                    size = td[2].text
                    seeders = td[3].text
                    leechers = td[4].text
                    uploader = td[5].text
                    url = self.url + td[0].find("a")["href"]
                    list_of_urls.append(url)
                    my_dict["data"].append(
                        {
                            "name": name,
                            "size": size,
                            "date": date,
                            "seeders": seeders,
                            "leechers": leechers,
                            "uploader": uploader if uploader else None,
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
            url = self.url + "/all/torrents/{}/{}.html".format(query, page)
            return await self.parser_result(start_time, url, session, idx=6)

    async def parser_result(self, start_time, url, session, idx=1):
        htmls = await self.get_all_results(session, url)
        result, urls = self._parser(htmls, idx)
        if result:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return result

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/movies/recent.html"
            else:
                if category == "apps":
                    category = "software"
                elif category == "tv":
                    category = "television"
                elif category == "books":
                    category = "ebooks"
                url = self.url + "/{}/recent.html".format(category)
            return await self.parser_result(start_time, url, session)

import asyncio
import re
import time
import aiohttp
from bs4 import BeautifulSoup
from scrapers import BaseScraper, HEADER_AIO, asyncio_fix


class Torlock(BaseScraper):
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
                    tm = soup.find_all("a")
                    magnet = tm[20]["href"]
                    torrent = tm[23]["href"]
                    try:
                        obj["poster"] = soup.find_all("img", class_="img-responsive")[
                            0
                        ]["src"]
                    except:
                        ...
                    if str(magnet).startswith("magnet") and str(torrent).endswith(
                        "torrent"
                    ):
                        obj["torrent"] = torrent
                        obj["magnet"] = magnet
                        obj["hash"] = re.search(
                            r"([{a-f\d,A-F\d}]{32,40})\b", magnet
                        ).group(0)
                        obj["category"] = tm[25].text
                        imgs = soup.select(".tab-content img.img-fluid")
                        if imgs and len(imgs) > 0:
                            obj["screenshot"] = [img["src"] for img in imgs]
                    else:
                        del obj
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

    def _parser(self, htmls, idx=0):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}

                for tr in soup.find_all("tr")[idx:]:
                    td = tr.find_all("td")
                    if len(td) == 0:
                        continue
                    name = td[0].get_text(strip=True)
                    if name != "":
                        url = td[0].find("a")["href"]
                        if url == "":
                            break
                        url = self.url + url
                        list_of_urls.append(url)
                        size = td[2].get_text(strip=True)
                        date = td[1].get_text(strip=True)
                        seeders = td[3].get_text(strip=True)
                        leechers = td[4].get_text(strip=True)
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
                try:
                    ul = soup.find("ul", class_="pagination")
                    tpages = ul.find_all("a")[-2].text
                    current_page = (
                        (ul.find("li", class_="active")).find("span").text.split(" ")[0]
                    )
                    my_dict["current_page"] = int(current_page)
                    my_dict["total_pages"] = int(tpages)
                except:
                    my_dict["current_page"] = None
                    my_dict["total_pages"] = None
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            url = self.url + "/all/torrents/{}.html?sort=seeds&page={}".format(
                query, page
            )
            return await self.parser_result(start_time, url, session, idx=5)

    async def parser_result(self, start_time, url, session, idx=0):
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
            if not category:
                url = self.url
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + "/{}.html".format(category)
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.limit = limit
            if not category:
                url = self.url + "/fresh.html"
            else:
                if category == "books":
                    category = "ebooks"
                url = self.url + "/{}/{}/added/desc.html".format(category, page)
            return await self.parser_result(start_time, url, session)

    #! Maybe impelment Search By Category in Future

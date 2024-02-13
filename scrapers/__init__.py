import os
import sys
import asyncio
from utils import asyncio_fix


HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
HEADER_AIO = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Cookie": "fencekey=8e5j3p61b3k0a9b0e44c5bbcecafaa5a2",
}


class BaseScraper:
    """Scraper class for scraping html"""

    def __init__(self):
        pass

    @asyncio_fix
    async def _get_html(self, session, url):
        try:
            async with session.get(url, headers=HEADER_AIO, proxy=HTTP_PROXY) as r:
                return await r.text()
        except:
            return None

    async def get_all_results(self, session, url):
        """Get all results from url"""
        return await asyncio.gather(asyncio.create_task(self._get_html(session, url)))

    async def search(self, query, page, limit):
        """Search method for searching torrents"""
        raise NotImplementedError

    async def trending(self, category, page, limit):
        """Trending method for getting trending torrents"""
        raise NotImplementedError

    async def recent(self, category, page, limit):
        """Recent method for getting recent torrents"""
        raise NotImplementedError


def asyncio_fix(func):
    """Decorator for fixing asyncio bug on windows"""

    def wrapper(*args):
        if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return func(*args)

    return wrapper

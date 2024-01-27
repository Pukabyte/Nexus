from pydantic import BaseModel
from typing import List, Optional


class SiteInfo(BaseModel):
    """Base Model for Site Info"""
    website: str
    trending_available: bool = False
    trending_category: bool = False
    search_by_category: bool = False
    recent_available: bool = False
    recent_category_available: bool = False
    categories: Optional[List[str]] = None
    limit: int = 0

class X1337(SiteInfo):
    """`1337x.to` Site Info"""
    website: str = "https://1337x.to"
    trending_available: bool = True
    trending_category: bool = True
    search_by_category: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "documentaries",
        "other",
        "xxx",
        "movies",
    ]
    limit: int = 100

class Torlock(SiteInfo):
    """`Torlock.com` Site Info"""
    website: str = "https://www.torlock.com"
    trending_available: bool = True
    trending_category: bool = True
    search_by_category: bool = False
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "documentaries",
        "other",
        "xxx",
        "movies",
        "books",
        "images",
    ]
    limit: int = 50

class Zooqle(SiteInfo):
    """`Zooqle.com` Site Info"""
    website: str = "https://zooqle.com"
    limit: int = 30

class MagnetDL(SiteInfo):
    """`MagnetDL.com` Site Info"""
    website: str = "https://www.magnetdl.com"
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = ["apps", "movies", "music", "games", "tv", "books"]
    limit: int = 40

class TorrentGalaxy(SiteInfo):
    """`TorrentGalaxy.to` Site Info"""
    website: str = "https://torrentgalaxy.to"
    trending_available: bool = True
    trending_category: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "documentaries",
        "other",
        "xxx",
        "movies",
        "books",
    ]
    limit: int = 50

class NyaaSi(SiteInfo):
    """`Nyaa.si` Site Info"""
    website: str = "https://nyaa.si"
    recent_available: bool = True
    limit: int = 50

class PirateBay(SiteInfo):
    """`ThePirateBay.org` Site Info"""
    website: str = "https://thepiratebay10.org"
    trending_available: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = ["tv"]
    limit: int = 50

class Bitsearch(SiteInfo):
    """`Bitsearch.to` Site Info"""
    website: str = "https://bitsearch.to"
    trending_available: bool = True

class Kickass(SiteInfo):
    """`Kickass.to` Site Info"""
    website: str = "https://kickasstorrents.to"
    trending_available: bool = True
    trending_category: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "documentaries",
        "other",
        "xxx",
        "movies",
        "books",
    ]
    limit: int = 50

class Libgen(SiteInfo):
    """`Libgen.is` Site Info"""
    website: str = "https://libgen.is"

class Yts(SiteInfo):
    """`Yts.mx` Site Info"""
    website: str = "https://yts.mx"
    trending_available: bool = True
    recent_available: bool = True

class Limetorrent(SiteInfo):
    """`Limetorrents.pro` Site Info"""
    website: str = "https://www.limetorrents.pro"
    trending_available: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "other",
        "movies",
        "books",
    ]

class TorrentFunk(SiteInfo):
    """`TorrentFunk.com` Site Info"""
    website: str = "https://www.torrentfunk.com"
    trending_available: bool = True
    trending_category: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "xxx",
        "movies",
        "books",
    ]

class Glodls(SiteInfo):
    """`Glodls.to` Site Info"""
    website: str = "https://glodls.to"
    trending_available: bool = True
    recent_available: bool = True
    limit: int = 45

class TorrentProject(SiteInfo):
    """`TorrentProject2.com` Site Info"""
    website: str = "https://torrentproject2.com"

class YourBittorrent(SiteInfo):
    """`YourBittorrent.com` Site Info"""
    website: str = "https://yourbittorrent.com"
    trending_available: bool = True
    trending_category: bool = True
    recent_available: bool = True
    recent_category_available: bool = True
    categories: List[str] = [
        "anime",
        "music",
        "games",
        "tv",
        "apps",
        "xxx",
        "movies",
        "books",
        "pictures",
        "other",
    ]
    limit: int = 20

class Sites(BaseModel):
    """Access to all the sites!"""
    x1337: X1337 = X1337()
    torlock: Torlock = Torlock()
    zooqle: Zooqle = Zooqle()
    magnetdl: MagnetDL = MagnetDL()
    torrentgalaxy: TorrentGalaxy = TorrentGalaxy()
    nyaa: NyaaSi = NyaaSi()
    piratebay: PirateBay = PirateBay()
    bitsearch: Bitsearch = Bitsearch()
    kickass: Kickass = Kickass()
    libgen: Libgen = Libgen()
    yts: Yts = Yts()
    limetorrent: Limetorrent = Limetorrent()
    torrentfunk: TorrentFunk = TorrentFunk()
    glodls: Glodls = Glodls()
    torrentproject: TorrentProject = TorrentProject()
    yourbittorrent: YourBittorrent = YourBittorrent()

    def __getitem__(self, key: str) -> SiteInfo:
        """Returns a site instance by name."""
        return getattr(self, key)

    def keys(self):
        """Returns a list of all site names (keys), excluding internal and special attributes."""
        return [
            attr for attr in dir(self)
            if not attr.startswith("__")
            and not callable(getattr(self, attr))
            and not attr.startswith("_")
        ]

    def __iter__(self):
        """Allows iteration over the site names."""
        for key in self.keys():
            yield key

    def items(self):
        """Returns a list of tuples (site_name, site_instance) for all sites."""
        return [(key, getattr(self, key)) for key in self.keys()]

    def values(self):
        """Returns a list of all site instances."""
        return [getattr(self, key) for key in self.keys()]


sites = Sites()

####  Example usage :)

# from utils.sites import sites
# url = sites["x1337"].website
# print(url)  # Output: https://1337x.to
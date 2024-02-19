from typing import List, Optional

from pydantic import BaseModel


class Torrent(BaseModel):
    title: str
    infohash: str
    size: Optional[str] = None
    seeders: Optional[str] = None
    leechers: Optional[str] = None
    category: Optional[str] = None
    parsed_data: Optional[dict] = None


class Torrents(BaseModel):
    site: str
    torrents: List[Torrent]

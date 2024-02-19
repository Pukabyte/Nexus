import time
from asyncio import gather, Semaphore
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from utils.sites import sites
from utils.realdebrid import realdebrid
from utils.logger import logger


search = APIRouter(tags=["Search Torrents"], prefix="/search")


@search.get("/")
async def search_torrents(
    query: str,
    site: Optional[str] = None,
    limit: int = Query(default=10, ge=1),
    page: int = Query(default=1, ge=1)
):
    """Search torrents from all available sites."""

    start_time = time.perf_counter()

    if site and site not in sites:
        raise HTTPException(status_code=404, detail=f"Site '{site}' not found.")

    semaphore = Semaphore(10)
    async def search_site(site_name):
        async with semaphore:
            return await sites[site_name].search(query, page=page, limit=limit)

    if site:
        tasks = [search_site(site)]
    else:
        tasks = [search_site(site_name) for site_name in sites.keys()]

    logger.info(f"Searching for '{query}' on {site or 'all sites'}")
    search_results = await gather(*tasks, return_exceptions=True)
    flat_results = [torrent for result in search_results if isinstance(result, dict) for torrent in result.get("data", []) if "infohash" in torrent]
    infohashes = list({torrent["infohash"].upper() for torrent in flat_results if torrent.get("infohash")})
    logger.info(f"Found {len(infohashes)} torrents from {len(search_results)} sites.")

    logger.info(f"Fetching cached results from Real-Debrid.")
    cached_infohashes = await realdebrid.fetch_cached(infohashes, batch_size=20)
    cached_torrents = [torrent for torrent in flat_results if torrent.get("infohash") and torrent["infohash"].upper() in cached_infohashes]
    logger.info(f"Found {len(cached_infohashes)} total cached torrents.")

    if not cached_torrents:
        raise HTTPException(status_code=204, detail="No cached results found.")

    elapsed_time = time.perf_counter() - start_time

    return {
        "data": cached_torrents[:limit],
        "total": len(flat_results),
        "total_cached": len(cached_torrents),
        "time": elapsed_time.__round__(2),
    }

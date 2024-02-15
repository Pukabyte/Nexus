import asyncio
import time
from fastapi import APIRouter, HTTPException, Query
from utils.sites import sites
from typing import Optional
from asyncio import create_task

search = APIRouter(tags=["Search Torrents"], prefix="/search")

@search.get("/")
async def search_torrents(
    query: str,
    site: Optional[str] = None,
    limit: Optional[int] = Query(default=10, ge=1),
    page: Optional[int] = Query(default=1, ge=1),
):
    """
    Search torrents by query string across all supported sites or a specific site.

    :param query: The search query string.
    :param site: Optional. The name of the specific site to search on.
    :param limit: Optional. The maximum number of results per page.
    :param page: Optional. The page number of results to retrieve.
    :return: Combined search results from all sites.
    """
    start_time = time.time()
    query = query.title()
    tasks = []

    if site and site not in sites.keys():
        raise HTTPException(status_code=404, detail=f"Site '{site}' not found.")

    if site:
        if site_instance := sites[site]:
            tasks.append(create_task(site_instance.search(query, page=page, limit=limit)))
    else:
        for _, site_instance in sites.items():
            tasks.append(create_task(site_instance.search(query, page=page, limit=limit)))

    search_results = await asyncio.gather(*tasks)
    combined_results = {"data": [], "total": 0}

    for result in search_results:
        if result and result.get("data"):
            combined_results["data"].extend(result["data"])
            combined_results["total"] += len(result["data"])

    combined_results["time"] = time.time() - start_time
    if not combined_results["data"]:
        raise HTTPException(status_code=404, detail="No results found.")

    return combined_results
import time
import asyncio
from fastapi import APIRouter, status, HTTPException
from typing import Optional
from utils.sites import sites


recent = APIRouter(tags=["Recent Torrents Route"], prefix="/recent")


@recent.get("/")
async def get_recent(
    site: Optional[str] = None,
    limit: Optional[int] = 0,
    category: Optional[str] = None,
    page: Optional[int] = 1,
):
    start_time = time.time()
    all_sites = sites

    if site:
        site = site.lower()
        category = category.lower() if category is not None else None
        return await fetch_recent_for_site(site, category, page, limit, all_sites)
    else:
        return await fetch_recent_from_all_sites(limit, all_sites, start_time)


async def fetch_recent_for_site(site, category, page, limit, all_sites):
    if site in all_sites and all_sites[site]["recent_available"]:
        limit = (
            all_sites[site]["limit"]
            if limit == 0 or limit > all_sites[site]["limit"]
            else limit
        )
        if category and category not in all_sites[site]["categories"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected category not available.",
            )
        return await all_sites[site]["website"]().recent(category, page, limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recent search not available for {site}.",
        )


async def fetch_recent_from_all_sites(limit, all_sites, start_time):
    sites_list = [
        site for site, config in all_sites.items() if config["recent_available"]
    ]
    tasks = [
        asyncio.create_task(all_sites[site]["website"]().recent(None, 1, limit))
        for site in sites_list
    ]
    results = await asyncio.gather(*tasks)

    COMBO = {"data": [], "total": 0, "time": 0}
    for res in results:
        if res and res["data"]:
            COMBO["data"].extend(res["data"])
            COMBO["total"] += res["total"]

    COMBO["time"] = time.time() - start_time
    if COMBO["total"] == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No recent torrents found."
        )

    return COMBO

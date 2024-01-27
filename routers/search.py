from time import time
from asyncio import gather, create_task
from fastapi import APIRouter, status
from fastapi import status
from utils import error_handler
from utils.sites import Sites
from typing import Optional


search = APIRouter(tags=["Search"], prefix="/search")

@search.get("/")
async def get_search_combo(query: str, limit: Optional[int] = 0):
    start_time = time()
    query = query.lower()
    all_sites = Sites
    sites_list = list(all_sites.keys())
    tasks = []
    COMBO = {"data": []}
    total_torrents_overall = 0
    for site in sites_list:
        limit = (
            all_sites[site]["limit"]
            if limit == 0 or limit > all_sites[site]["limit"]
            else limit
        )
        tasks.append(
            create_task(
                all_sites[site]["website"]().search(query, page=1, limit=limit)
            )
        )
    results = await gather(*tasks)
    for res in results:
        if res is not None and len(res["data"]) > 0:
            for torrent in res["data"]:
                COMBO["data"].append(torrent)
            total_torrents_overall = total_torrents_overall + res["total"]
    COMBO["time"] = time() - start_time
    COMBO["total"] = total_torrents_overall
    if total_torrents_overall == 0:
        return error_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            json_message={"error": "Result not found."},
        )
    return COMBO

@search.get("/{query}/{limit}/{page}")
async def search_for_torrents(
    query: str, limit: Optional[int] = 0, page: Optional[int] = 1
):
    site = site.lower()
    query = query.lower()
    all_sites = Sites
    if all_sites:
        limit = (
            all_sites[site]["limit"]
            if limit == 0 or limit > all_sites[site]["limit"]
            else limit
        )

        resp = await all_sites[site]["website"]().search(query, page, limit)
        if resp is None:
            return error_handler(
                status_code=status.HTTP_403_FORBIDDEN,
                json_message={"error": "Website Blocked Change IP or Website Domain."},
            )
        elif len(resp["data"]) > 0:
            return resp
        else:
            return error_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                json_message={"error": "Result not found."},
            )

    return error_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        json_message={"error": "Selected Site Not Available"},
    )

@search.get("/{site}/{query}")
async def get_torrent_from_site(site: str, url: str):
    site = site.lower()
    all_sites = Sites
    if all_sites:
        resp = await all_sites[site]["website"]().get_torrent_by_url(url)
        if resp is None:
            return error_handler(
                status_code=status.HTTP_403_FORBIDDEN,
                json_message={"error": "Website Blocked Change IP or Website Domain."},
            )
        elif len(resp["data"]) > 0:
            return resp
        else:
            return error_handler(
                status_code=status.HTTP_404_NOT_FOUND,
                json_message={"error": "Result not found."},
            )
    return error_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        json_message={"error": "Selected Site Not Available"},
    )

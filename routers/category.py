from fastapi import APIRouter, HTTPException, status
from typing import Optional
from utils.sites import sites

category = APIRouter(tags=["Category Torrents Route"], prefix="/category")


@category.get("/{site}/{query}/{category}/{limit}/{page}")
async def get_category(
    site: str,
    query: str,
    category: str,
    limit: Optional[int] = 0,
    page: Optional[int] = 1,
):
    site = site.lower()
    query = query.lower()
    category = category.lower()
    site_info = sites.get(site)

    if not site_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Selected Site Not Available"
        )

    limit = site_info.limit if limit == 0 or limit > site_info.limit else limit

    if not site_info.category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category search not available for {site}.",
        )

    if category not in site_info.categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected category not available.",
            headers={"available_categories": site_info.categories},
        )

    scraper_instance = site_info.website()
    resp = await scraper_instance.category(query, category, page, limit)

    if resp is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Website Blocked. Change IP or Website Domain.",
        )

    if len(resp.get("data", [])) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Result not found."
        )

    return resp

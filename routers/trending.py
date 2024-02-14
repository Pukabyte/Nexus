from fastapi import APIRouter, HTTPException, status
from typing import Optional
from utils.sites import sites

trending = APIRouter(tags=["Trending Torrents"], prefix="/trending")


@trending.get("/")
async def get_trending(
    site: Optional[str] = None,
    limit: Optional[int] = 0,
    category: Optional[str] = None,
    page: Optional[int] = 1,
):
    if not site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'site' parameter is missing. Please provide the 'site' parameter in the request URL.",
        )

    site = site.title()
    site_info = sites.get(site)

    if not site_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Selected Site Not Available"
        )

    limit = site_info.limit if limit == 0 or limit > site_info.limit else limit

    if not site_info.trending_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trending search not available for {site}.",
        )

    if category is not None:
        category = category.lower()
        if not site_info.trending_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Search by trending category not available for {site}.",
            )
        if category not in site_info.categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected category not available.",
                headers={"available_categories": site_info.categories},
            )

    scraper_instance = site_info.website()
    resp = await scraper_instance.trending(category, page, limit)

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

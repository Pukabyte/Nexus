from fastapi import APIRouter, HTTPException, status
from typing import Optional
from utils.sites import sites

trending = APIRouter(tags=["Trending Torrents"], prefix="/trending")

@trending.get("/")
async def get_trending(
    site: Optional[str] = None,
    limit: Optional[int] = 25,
    category: Optional[str] = None,
    page: Optional[int] = 1,
):
    if not site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'site' parameter is missing. Please provide the 'site' parameter in the request URL.",
        )

    site_key = site.lower()
    site_info = sites.get(site_key)

    if not site_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site '{site}' not found. Please check the site parameter.",
        )

    if not site_info.trending_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trending search not available for {site}.",
        )

    if category:
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
                headers={"available_categories": ", ".join(site_info.categories)},  # Ensure the header value is a string
            )

    scraper_instance = site_info.get_scraper_instance()
    if not scraper_instance:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize the scraper instance for {site}.",
        )

    resp = await scraper_instance.trending(category, page, limit)
    if resp is None or 'error' in resp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trending data found or an error occurred.",
        )

    return resp

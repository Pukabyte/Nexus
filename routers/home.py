from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from utils import error_handler
from utils.settings import VERSION
from utils.sites import sites


base = APIRouter(tags=["Home Route"], prefix="")


@base.get("/")
def root(req: Request):
    """Health route for checking the health of the api"""
    return JSONResponse(
        {
            "app": "Nexus",
            "version": VERSION,
            "ip": req.client.host,
        }
    )


@base.get("/health")
def health_route():
    """Get OK response for checking if the api is up and running"""
    return JSONResponse(
        {
            "message": "OK",
        }
    )


@base.get("/sites")
async def get_all_supported_sites():
    supported_sites = {}

    for site_name, site_info in sites.items():
        supported_sites[site_name] = {
            "trending_available": site_info.trending_available,
            "recent_available": site_info.recent_available,
            "categories": site_info.categories if hasattr(site_info, "categories") else None
        }

    return error_handler(
        status_code=status.HTTP_200_OK,
        json_message={
            "supported_sites": supported_sites,
        },
    )
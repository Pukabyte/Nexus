from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from utils.realdebrid import realdebrid
from utils import error_handler


rdebrid = APIRouter(tags=["Real Debrid"], prefix="/rd")


@rdebrid.get("/user")
def instant_avail_check(req: Request):
    """Check hosts availability"""
    response = realdebrid.user.get()
    if response.status_code == 200:
        data = response.json()
        return JSONResponse(
            {
                "status": "OK",
                "data": data,
            }
        )
    else:
        return error_handler.handle_error(response.status_code)


@rdebrid.get("/system/time")
def system_time(req: Request):
    """Get server time"""
    response = realdebrid.system.time()
    if response.status_code == 200:
        data = response.json()
        return JSONResponse({"status": "OK", "data": data})
    else:
        return error_handler.handle_error(response.status_code)


@rdebrid.get("/system/disable_token")
def disable_token(req: Request):
    """Disable access token"""
    response = realdebrid.system.disable_token()
    if response.status_code == 204:  # No content
        return JSONResponse({"status": "OK", "message": "Token disabled successfully"})
    else:
        return error_handler.handle_error(response.status_code)


@rdebrid.get("/torrents/instantAvailability")
def instant_availability(req: Request, hashes: str = Query(...)):
    """Check instant availability for torrent hashes"""
    hashes_list = hashes.split("/")
    results = {}
    for hash in hashes_list:
        response = realdebrid.torrents.instant_availability(hash)
        if response.status_code == 200:
            data = response.json()
            results[hash] = data
        else:
            results[hash] = error_handler.parse_error(response)
    return JSONResponse({"status": "OK", "data": results})

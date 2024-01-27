from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import asyncio
import sys


HEADER_AIO = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    "Cookie": "fencekey=8e5j3p61b3k0a9b0e44c5bbcecafaa5a2",
}

def error_handler(status_code, json_message):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(json_message),
    )

def decorator_asyncio_fix(func):
    def wrapper(*args):
        if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return func(*args)
    return wrapper

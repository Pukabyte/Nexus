import asyncio
import sys

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def error_handler(status_code, json_message):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(json_message),
    )


def asyncio_fix(func):
    """Decorator for fixing asyncio bug on windows"""

    def wrapper(*args):
        if (
            sys.version_info[0] == 3
            and sys.version_info[1] >= 8
            and sys.platform.startswith("win")
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return func(*args)

    return wrapper

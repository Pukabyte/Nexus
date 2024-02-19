import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.settings import VERSION

from routers.home import base
from routers.search import search
from routers.trending import trending
from routers.recent import recent


app = FastAPI(
    title="Nexus",
    version=VERSION,
    description="On Demand Cache Real-Debrid Indexer",
    docs_url="/docs",
    contact={"name": "Nexus", "url": "https://github.com/Pukabyte/Nexus"},
)

app.include_router(base)
app.include_router(search)
app.include_router(trending)
app.include_router(recent)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8978)

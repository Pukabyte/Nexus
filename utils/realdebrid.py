import aiohttp

from utils.logger import logger
from utils.request import get
from utils.settings import settings


class RD:
    """Real Debrid class for Real Debrid API operations"""

    def __init__(self):
        self.rd_key = settings.get("RD_APITOKEN")
        if not self.rd_key:
            logger.error(
                "Real Debrid API Key not found. Please add it to .env or environment variables."
            )
            return
        self.rd_url = "https://api.real-debrid.com/rest/1.0"
        self.header = {"Authorization": "Bearer " + str(self.rd_key)}
        self.initialized = self.validate()
        if not self.initialized:
            logger.error("Real Debrid API not initialized.")
            return

        self.session = None
        logger.info("Real Debrid API initialized.")

    def validate(self):
        """Validate the Real Debrid API key by making a test request."""
        try:
            response = get(self.rd_url + "/user", additional_headers=self.header)
            if not response.status_code == 200:
                logger.error("Real Debrid API Key is not valid.")
                return False
            if not response.data.type == "premium":
                logger.error("Real Debrid User is not Premium.")
                return False
            return True
        except Exception as e:
            logger.error(
                f"Exception occurred while validating Real Debrid API Key: {e}"
            )
            return False

    async def fetch_cached(self, infohashes, batch_size=20):
        """Fetch cached status of infohashes from Real Debrid."""
        cached_infohashes = set()
        for i in range(0, len(infohashes), batch_size):
            batch = infohashes[i : i + batch_size]
            cached_in_batch = await self._hash_check_batch(batch)
            cached_infohashes.update(cached_in_batch)
            logger.info(
                f"Found {len(cached_in_batch)} cached hashes from batch {i//batch_size+1}"
            )
        return cached_infohashes

    async def _hash_check_batch(self, infohash_batch):
        """Check a single batch of infohashes for cache status."""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        cached_infohashes = set()
        hashes_string = "/".join(infohash.lower() for infohash in infohash_batch)
        url = f"{self.rd_url}/torrents/instantAvailability/{hashes_string}"
        try:
            async with self.session.get(url, headers=self.header) as response:
                response.raise_for_status()
                json_response = await response.json()
                for infohash, data in json_response.items():
                    if "rd" in data and data["rd"]:
                        cached_infohashes.add(infohash.upper())
        except Exception as e:
            logger.error(f"Error checking cache status for batch: {e}")
        return cached_infohashes

    async def close(self):
        """Close aiohttp session if it's open."""
        if self.session:
            await self.session.close()


realdebrid = RD()

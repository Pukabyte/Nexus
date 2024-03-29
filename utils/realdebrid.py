import os
import time
import json
import requests
import itertools
from pathlib import Path
from utils.logger import logger
from utils.settings import settings


class RD:
    def __init__(self):
        self.rd_apitoken = settings.get("RD_APITOKEN")
        self.base_url = "https://api.real-debrid.com/rest/1.0"
        self.header = {"Authorization": "Bearer " + str(self.rd_apitoken)}
        self.error_codes = json.load(
            open(os.path.join(Path(__file__).parent.absolute(), "error_codes.json"))
        )
        self.sleep = int(os.getenv("SLEEP", 2000)) / 1000
        self.long_sleep = int(os.getenv("LONG_SLEEP", 30000)) / 1000
        self.count_obj = itertools.cycle(range(0, 501))
        self.count = next(self.count_obj)
        self.check_token()

        self.system = self.System(self)
        self.user = self.User(self)
        self.unrestrict = self.Unrestrict(self)
        self.traffic = self.Traffic(self)
        self.streaming = self.Streaming(self)
        self.downloads = self.Downloads(self)
        self.torrents = self.Torrents(self)

    def get(self, path, **options):
        request = requests.get(
            self.base_url + path, headers=self.header, params=options
        )
        return self.handler(request, self.error_codes, path)

    def post(self, path, **payload):
        request = requests.post(self.base_url + path, headers=self.header, data=payload)
        return self.handler(request, self.error_codes, path)

    def put(self, path, filepath, **payload):
        with open(filepath, "rb") as file:
            request = requests.put(
                self.base_url + path, headers=self.header, data=file, params=payload
            )
        return self.handler(request, self.error_codes, path)

    def delete(self, path):
        request = requests.delete(self.base_url + path, headers=self.header)
        return self.handler(request, self.error_codes, path)

    def handler(self, request, error_codes, path):
        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.error("%s at %s", errh, path)
        except requests.exceptions.ConnectionError as errc:
            logger.error("%s at %s", errc, path)
        except requests.exceptions.Timeout as errt:
            logger.error("%s at %s", errt, path)
        except requests.exceptions.RequestException as err:
            logger.error("%s at %s", err, path)
        try:
            if "error_code" in request.json():
                code = request.json()["error_code"]
                message = error_codes.get(str(code), "Unknown error")
                logger.warning("%s: %s at %s", code, message, path)
        except:
            pass
        self.handle_sleep()
        return request

    def check_token(self):
        if self.rd_apitoken is None:
            logger.warning("Add token to .env or environment variables.")

    def handle_sleep(self):
        if self.count < 500:
            logger.debug("Sleeping %ss", self.sleep)
            time.sleep(self.sleep)
        elif self.count == 500:
            logger.debug("Sleeping %ss", self.long_sleep)
            time.sleep(self.long_sleep)
            self.count = 0

    class System:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def disable_token(self):
            return self.rd.get("/disable_access_token")

        def time(self):
            return self.rd.get("/time")

        def iso_time(self):
            return self.rd.get("/time/iso")

    class User:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def get(self):
            return self.rd.get("/user")

    class Unrestrict:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def check(self, link, password=None):
            return self.rd.post("/unrestrict/check", link=link, password=password)

        def link(self, link, password=None, remote=None):
            return self.rd.post(
                "/unrestrict/link", link=link, password=password, remote=remote
            )

        def folder(self, link):
            return self.rd.post("/unrestrict/folder", link=link)

        def container_file(self, filepath):
            return self.rd.put("/unrestrict/containerFile", filepath=filepath)

        def container_link(self, link):
            return self.rd.post("/unrestrict/containerLink", link=link)

    class Traffic:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def get(self):
            return self.rd.get("/traffic")

        def details(self, start=None, end=None):
            return self.rd.get("/traffic/details", start=start, end=end)

    class Streaming:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def transcode(self, id):
            return self.rd.get("/streaming/transcode/" + str(id))

        def media_info(self, id):
            return self.rd.get("/streaming/mediaInfos/" + str(id))

    class Downloads:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def get(self, offset=None, page=None, limit=None):
            return self.rd.get("/downloads", offset=offset, page=page, limit=limit)

        def delete(self, id):
            return self.rd.delete("/downloads/delete/" + str(id))

    class Torrents:
        def __init__(self, rd_instance):
            self.rd = rd_instance

        def get(self, offset=None, page=None, limit=None, filter=None):
            return self.rd.get(
                "/torrents", offset=offset, page=page, limit=limit, filter=filter
            )

        def info(self, id):
            return self.rd.get("/torrents/info/" + str(id))

        def instant_availability(self, hash):
            return self.rd.get("/torrents/instantAvailability/" + str(hash))

        def active_count(self):
            return self.rd.get("/torrents/activeCount")

        def available_hosts(self):
            return self.rd.get("/torrents/availableHosts")

        def add_file(self, filepath, host=None):
            return self.rd.put("/torrents/addTorrent", filepath=filepath, host=host)

        def add_magnet(self, magnet, host=None):
            magnet_link = "magnet:?xt=urn:btih:" + str(magnet)
            return self.rd.post("/torrents/addMagnet", magnet=magnet_link, host=host)

        def select_files(self, id, files):
            return self.rd.post("/torrents/selectFiles/" + str(id), files=str(files))

        def delete(self, id):
            return self.rd.delete("/torrents/delete/" + str(id))


realdebrid = RD()

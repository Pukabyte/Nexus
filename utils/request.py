import json
from types import SimpleNamespace

import requests
import xmltodict
from lxml import etree
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils import logger

retry_strategy = Retry(
    total=2,
    status_forcelist=[500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)

DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class ResponseObject:
    def __init__(self, response: requests.Response, response_type=SimpleNamespace):
        self.response = response
        self.is_ok = response.ok
        self.status_code = response.status_code
        self.response_type = response_type
        self.data = self.handle_response(response)

    def handle_response(self, response: requests.Response):
        if not self.is_ok and self.status_code not in [429, 520, 522, 401]:
            logger.warning("Error %s: %s", response.status_code, response.content)
        if self.status_code in [520, 522]:
            raise requests.exceptions.ConnectTimeout(response.content)
        if self.status_code not in [200, 201, 204]:
            if self.status_code in [429]:
                raise requests.exceptions.RequestException(response.content)
            if self.status_code == 401:
                raise response.raise_for_status()
            return {}

        if len(response.content) > 0:
            if "handler error" not in response.text:
                content_type = response.headers.get("Content-Type")
                if "application/rss+xml" in content_type or "text/xml" in content_type:
                    if self.response_type == dict:
                        return xmltodict.parse(response.content)
                    return self.xml_to_simplenamespace(response.content)
                if "application/json" in content_type:
                    if self.response_type == dict:
                        return json.loads(response.content)
                    return json.loads(
                        response.content,
                        object_hook=lambda item: SimpleNamespace(**item),
                    )
        return {}

    def xml_to_simplenamespace(self, xml_string):
        root = etree.fromstring(xml_string)

        def element_to_simplenamespace(element):
            children_as_ns = {
                child.tag: element_to_simplenamespace(child) for child in element
            }
            attributes = {key: value for key, value in element.attrib.items()}
            attributes.update(children_as_ns)
            return SimpleNamespace(**attributes, text=element.text)

        return element_to_simplenamespace(root)


def handle_request_exception() -> SimpleNamespace:
    logger.error("Request failed", exc_info=True)
    return SimpleNamespace(ok=False, data={}, content={}, status_code=500)


def make_request(
    method: str,
    url: str,
    data: dict = None,
    timeout=5,
    additional_headers=None,
    retry_if_failed=True,
    response_type=SimpleNamespace,
) -> ResponseObject:
    session = requests.Session()
    if retry_if_failed:
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    headers = DEFAULT_HEADERS.copy()
    if additional_headers:
        headers.update(additional_headers)

    try:
        response = session.request(
            method, url, headers=headers, data=data, timeout=timeout
        )
    except requests.RequestException:
        response = handle_request_exception()

    session.close()
    return ResponseObject(response, response_type)


def ping(url: str, timeout=10, additional_headers=None):
    return requests.Session().get(url, headers=additional_headers, timeout=timeout)


def get(
    url: str,
    timeout=10,
    data=None,
    additional_headers=None,
    retry_if_failed=True,
    response_type=SimpleNamespace,
) -> ResponseObject:
    return make_request(
        "GET",
        url,
        data=data,
        timeout=timeout,
        additional_headers=additional_headers,
        retry_if_failed=retry_if_failed,
        response_type=response_type,
    )


def post(
    url: str, data: dict, timeout=10, additional_headers=None, retry_if_failed=False
) -> ResponseObject:
    return make_request(
        "POST",
        url,
        data=data,
        timeout=timeout,
        additional_headers=additional_headers,
        retry_if_failed=retry_if_failed,
    )


def put(
    url: str,
    data: dict = None,
    timeout=10,
    additional_headers=None,
    retry_if_failed=False,
) -> ResponseObject:
    return make_request(
        "PUT",
        url,
        data=data,
        timeout=timeout,
        additional_headers=additional_headers,
        retry_if_failed=retry_if_failed,
    )

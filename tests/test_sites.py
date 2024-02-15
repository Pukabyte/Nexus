import pytest
from requests.exceptions import RequestException, ReadTimeout
from utils.request import ping
from utils.sites import sites


@pytest.mark.asyncio
async def test_sites_total():
    try:
        assert len(sites) == 16
    except AssertionError:
        pytest.fail("Number of sites has changed. Update the tests.")


@pytest.mark.asyncio
async def test_ping_all_sites():
    for site_name in sites.keys():
        site_instance = sites[site_name]
        try:
            response = ping(site_instance.website, timeout=5)
            print(f"{site_instance.scraper_class}: {'UP' if response else 'DOWN'}")
        except ReadTimeout:
            pytest.skip(f"{site_instance.scraper_class}: DOWN (Timeout)")
        except NotImplementedError:
            pytest.skip(f"{site_instance.scraper_class}: Not implemented for Ping.")
        except RequestException as e:
            pytest.warns(f"Unexpected Ping error with {site_name}: {e}")


@pytest.mark.asyncio
async def test_search_all_sites():
    query = "test_query"
    page = 1
    limit = 10
    for site_name in sites.keys():
        site_instance = sites[site_name]
        try:
            result = await site_instance.search(query, page, limit)
            assert result is not None
        except NotImplementedError:
            pytest.skip(f"{site_name.title()} not implemented for Search.")
        # except Exception as e:
        #     pytest.fail(f"Unexpected Search error with {site_name}: {e}")


@pytest.mark.asyncio
async def test_trending_all_sites():
    for site_name in sites.keys():
        site_instance = sites[site_name]
        try:
            if hasattr(site_instance, "trending") and callable(
                getattr(site_instance, "trending")
            ):
                result = await site_instance.trending("movies", 1, 2)
                print(f"Result for {site_name}: {result}")  # Add logging here
                assert result is not None
        except NotImplementedError:
            pass


# @pytest.mark.asyncio
# async def test_recent_all_sites():
#     category = "test_category"
#     page = 1
#     limit = 10
#     for site_name in sites.keys():
#         site_instance = sites[site_name]
#         try:
#             result = await site_instance.recent(category, page, limit)
#             assert result is not None
#         except NotImplementedError:
#             pass
#         except Exception as e:
#             pytest.warns(f"Unexpected Recent error with {site_name}: {e}")

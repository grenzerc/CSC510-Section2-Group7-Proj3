"""Use Case #13 -- View driver delivery statistics.

Drivers can read their own statistics; other accounts and anonymous requests
must not be able to read them.
"""

import urllib.parse

import pytest

from api_helpers import api_request, register_and_login, require_backend


@pytest.fixture(scope="module", autouse=True)
def backend():
    require_backend()


def stats_path(username):
    return "/api/driverStats?" + urllib.parse.urlencode({"username": username})


def test_a_driver_can_read_their_own_statistics():
    """This proves the main success scenario."""
    driver, token = register_and_login("driver", "own_stats")

    status, body = api_request("GET", stats_path(driver["username"]), token=token)

    assert status == 200, body
    assert body["username"] == driver["username"]
    assert body["totalDeliveries"] == 0
    assert "totalEarning" in body


def test_driver_statistics_require_a_login():
    """This proves extension 2a: earnings are not public."""
    driver, _ = register_and_login("driver", "public_stats")

    status, body = api_request("GET", stats_path(driver["username"]))

    assert status == 401, f"driver statistics were served with no credentials: {status} {body}"


def test_one_driver_cannot_read_another_drivers_statistics():
    """This proves extension 2b: drivers cannot read another driver's earnings."""
    victim, _ = register_and_login("driver", "victim")
    _, snooper = register_and_login("driver", "snooper")

    status, body = api_request("GET", stats_path(victim["username"]), token=snooper)

    assert status == 403, f"one driver read another's earnings: {status} {body}"


def test_a_customer_cannot_read_driver_statistics():
    """This proves extension 2b for a non-driver account."""
    driver, _ = register_and_login("driver", "watched")
    _, customer = register_and_login("customer", "watcher")

    status, body = api_request("GET", stats_path(driver["username"]), token=customer)

    assert status == 403, f"a customer read driver earnings: {status} {body}"


def test_an_unknown_username_still_requires_login():
    """Authenticate before revealing whether statistics exist.

    Authorized missing-driver behavior is covered by DriverStatsSecurityTest.
    """
    status, body = api_request("GET", stats_path("nobody_by_this_name"))

    assert status == 401, f"expected 401 without credentials, got {status} {body}"

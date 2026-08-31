"""Use Case #13 -- View driver delivery statistics.

The happy path here works. Everything else in this file is about who else can
read it, which turns out to be everyone.
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
    """This proves extension 2a: earnings are not public.

    Expected to fail today. SpringSecurityConfig calls permitAll() on every GET
    under /api/driverStats, and DriverStatsController has no @PreAuthorize --
    the annotation is imported in that file and never used. No token needed.
    """
    driver, _ = register_and_login("driver", "public_stats")

    status, body = api_request("GET", stats_path(driver["username"]))

    assert status == 401, f"driver statistics were served with no credentials: {status} {body}"


def test_one_driver_cannot_read_another_drivers_statistics():
    """This proves extension 2b.

    Expected to fail today. The endpoint reads the username straight off the
    query string and never compares it to whoever is holding the token.
    """
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


def test_an_unknown_username_is_not_found():
    """This proves extension 2c.

    Expected to fail today. The controller returns 200 with whatever the
    service produced, so a caller cannot tell "no such driver" apart from
    "a driver who has not delivered anything yet".
    """
    status, body = api_request("GET", stats_path("nobody_by_this_name"))

    assert status == 404, f"expected 404 for an unknown driver, got {status} {body}"

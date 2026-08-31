import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

import pytest


API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8080")


def api_request(method, path, body=None, token=None):
    url = f"{API_BASE_URL}{path}"
    data = None
    headers = {"Content-Type": "application/json"}

    if body is not None:
        data = json.dumps(body).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            return response.status, parse_response(response_body)
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8")
        return error.code, parse_response(response_body)


def parse_response(response_body):
    if not response_body:
        return {}

    try:
        return json.loads(response_body)
    except json.JSONDecodeError:
        return {"raw": response_body}


def unique_user(prefix="user", role="customer"):
    timestamp_letters = base26_letters(int(time.time() * 1000))
    pid_letters = base26_letters(os.getpid())
    run_id = f"{timestamp_letters}_{pid_letters}"
    username = f"{prefix}_{run_id}"
    return {
        "username": username,
        "email": f"{username}@example.com",
        "password": "userpass123",
        "role": role,
    }


def base26_letters(number):
    letters = []

    while number:
        number, remainder = divmod(number, 26)
        letters.append(chr(ord("a") + remainder))

    return "".join(reversed(letters)) or "a"


def register_and_login(prefix, role):
    user = unique_user(prefix=prefix, role=role)
    reg_status, reg_body = api_request("POST", "/auth/register", user)
    assert reg_status == 200, reg_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {"username": user["username"], "password": user["password"]},
    )
    assert login_status == 200, login_body
    assert "accessToken" in login_body

    return user, login_body["accessToken"]


@pytest.fixture(scope="module", autouse=True)
def backend_is_running():
    try:
        status, _ = api_request(
            "POST",
            "/auth/login",
            {"username": "health_check", "password": "wrong-password"},
        )
    except urllib.error.URLError as error:
        pytest.fail(f"Backend is not reachable at {API_BASE_URL}: {error}")

    assert status in {400, 401, 403, 404}, (
        "Backend should answer auth requests, even when credentials are invalid"
    )


def test_unauthenticated_request_rejected_from_admin_only_endpoint():
    """This proves Use Case #5 Extension 2a and 4a:

    A request with no session token at all is rejected before it can reach
    an admin-restricted resource (the full user list).
    """
    status, body = api_request("GET", "/api/users")
    assert status == 401, body


def test_own_profile_endpoint_rejects_unauthenticated_access():
    """This proves Use Case #5 Extension 2a:

    A user who is not logged in cannot load any authenticated page's data,
    not even their own profile -- matching the "redirected to login" flow.
    """
    status, body = api_request("GET", "/api/users/me")
    assert status == 401, body


def test_unauthenticated_request_rejected_from_role_restricted_order_endpoint():
    """This proves Use Case #5 Extension 4a:

    An API request made without a valid token against a role-restricted
    resource (a customer's own orders) is rejected rather than served.
    """
    status, body = api_request("GET", "/api/orders/my-orders")
    assert status in {401, 403}, body


def test_customer_blocked_from_admin_only_endpoint():
    """This proves Use Case #5 Extension 3b and main success scenario
    steps 2-4:

    A logged-in customer is authenticated but not authorized for the
    admin-only user list, so access is blocked.
    """
    user, token = register_and_login("restrict_uc_cust_admin", "customer")

    status, body = api_request("GET", "/api/users", token=token)
    assert status == 403, body


def test_customer_blocked_from_driver_or_admin_order_endpoint():
    """This proves Use Case #5 Extension 3a and main success scenario
    steps 2-4:

    A logged-in customer is denied access to the driver/admin-only
    available-orders resource.
    """
    user, token = register_and_login("restrict_uc_cust_orders", "customer")

    status, body = api_request("GET", "/api/orders/availableOrders", token=token)
    assert status == 403, body


def test_driver_stats_endpoint_allows_unauthenticated_access():
    """This proves Use Case #5 Precondition 2 and Extension 4a:

    A driver's dashboard statistics should be a restricted resource that
    rejects requests without a valid token, the same way /api/users and
    /api/orders/my-orders do.

    KNOWN DEFECT: DriverStatsController.getDriverStats has no @PreAuthorize
    annotation, and SpringSecurityConfig explicitly permitAll()s GET
    /api/driverStats/**. The endpoint therefore returns a driver's earnings,
    delivery count, and rating to anyone, authenticated or not. This test is
    expected to FAIL until the endpoint is locked down like the other
    dashboard data endpoints.
    """
    driver, _ = register_and_login("restrict_uc_driver_stats", "driver")

    status, body = api_request(
        "GET", "/api/driverStats?" + urllib.parse.urlencode({"username": driver["username"]})
    )
    assert status == 401, body


def test_customer_blocked_from_viewing_driver_dashboard_stats():
    """This proves Use Case #5 Extension 3a:

    A logged-in customer should be blocked from viewing driver-dashboard
    content, the same way they are blocked from the admin and
    driver/admin-only order endpoints.

    KNOWN DEFECT: because DriverStatsController.getDriverStats carries no
    role check at all, an authenticated customer can read any driver's
    stats by username, the same gap as the unauthenticated case above. This
    test is expected to FAIL until the endpoint enforces the driver/admin
    role restriction the use case calls for.
    """
    driver, _ = register_and_login("restrict_uc_target_driver", "driver")
    customer, customer_token = register_and_login("restrict_uc_cust_stats", "customer")

    status, body = api_request(
        "GET",
        "/api/driverStats?" + urllib.parse.urlencode({"username": driver["username"]}),
        token=customer_token,
    )
    assert status == 403, body

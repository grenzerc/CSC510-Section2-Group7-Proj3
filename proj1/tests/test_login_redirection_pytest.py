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


def error_text(body):
    """Errors may surface under an 'error' key (AuthServiceImpl validation)
    or a 'message' key (GlobalExceptionHandler)."""
    return str(body.get("error") or body.get("message") or body)


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


def test_login_authenticates_valid_credentials_and_returns_session_token():
    """This proves Use Case #4 main success scenario steps 1-4 and
    Postconditions 1 and 2:

    A user with a registered account can submit valid credentials, have them
    authenticated, and receive a session token the frontend can store.
    """
    user, token = register_and_login("login_uc_main", "customer")
    assert token


def test_rejects_login_with_invalid_credentials():
    """This proves Use Case #4 Extension 2a:

    Login with an incorrect password is rejected and no session token is
    issued.
    """
    user = unique_user(prefix="login_uc_badcreds")
    reg_status, reg_body = api_request("POST", "/auth/register", user)
    assert reg_status == 200, reg_body

    status, body = api_request(
        "POST",
        "/auth/login",
        {"username": user["username"], "password": "totally-wrong-password"},
    )
    assert status in {400, 401, 403}, body
    assert "accessToken" not in body


def test_login_identifies_role_for_customer_redirection():
    """This proves Use Case #4 main success scenario step 5 and
    Extension 6d:

    After login, the backend reports ROLE_CUSTOMER for a customer account,
    which is what the frontend uses to redirect to the customer dashboard.
    """
    user, token = register_and_login("login_uc_cust_role", "customer")

    status, body = api_request("GET", "/api/users/me", token=token)
    assert status == 200, body
    assert body["username"] == user["username"]
    assert body["role"] == "ROLE_CUSTOMER"


def test_login_identifies_role_for_driver_redirection():
    """This proves Use Case #4 Extension 6c:

    After login, the backend reports ROLE_DRIVER for a driver account, which
    is what the frontend uses to redirect to the driver dashboard.
    """
    user, token = register_and_login("login_uc_driver_role", "driver")

    status, body = api_request("GET", "/api/users/me", token=token)
    assert status == 200, body
    assert body["role"] == "ROLE_DRIVER"


def test_login_identifies_role_for_staff_redirection():
    """This proves Use Case #4 Extension 6b:

    After login, the backend reports ROLE_STAFF for a staff account, which
    is what the frontend uses to redirect to the staff dashboard.
    """
    user, token = register_and_login("login_uc_staff_role", "staff")

    status, body = api_request("GET", "/api/users/me", token=token)
    assert status == 200, body
    assert body["role"] == "ROLE_STAFF"


def test_customer_can_access_role_appropriate_endpoint():
    """This proves Use Case #4 Postcondition 4:

    A logged-in customer can access an endpoint reserved for their own role
    (the customer's own orders).
    """
    user, token = register_and_login("login_uc_access_ok", "customer")

    status, body = api_request("GET", "/api/orders/my-orders", token=token)
    assert status == 200, body


def test_customer_is_blocked_from_admin_only_endpoint():
    """This proves Use Case #4 Postcondition 5 and Extension 6e:

    A logged-in customer is denied access to an admin-only endpoint (the
    full user list), so they cannot reach features outside their role.
    """
    user, token = register_and_login("login_uc_cust_blocked", "customer")

    status, body = api_request("GET", "/api/users", token=token)
    assert status == 403, body


def test_driver_is_blocked_from_customer_only_endpoint():
    """This proves Use Case #4 Postcondition 5 and Extension 6e:

    A logged-in driver is denied access to a customer-only endpoint (the
    customer's own orders), even though they are authenticated.
    """
    user, token = register_and_login("login_uc_driver_blocked", "driver")

    status, body = api_request("GET", "/api/orders/my-orders", token=token)
    assert status == 403, body


def test_unauthenticated_request_is_rejected_from_protected_endpoint():
    """This proves Use Case #4 Preconditions require a valid session:

    A request with no session token at all is rejected before any role or
    redirection logic runs.
    """
    status, body = api_request("GET", "/api/users/me")
    assert status == 401, body


def test_login_fails_for_account_with_no_valid_role():
    """This proves Use Case #4 Extension 5a:

    A user account not associated with a valid role should still be able to
    log in, receive a clear error, and not be redirected to a dashboard.

    KNOWN DEFECT: AuthServiceImpl.register silently accepts any role string
    it doesn't recognize (e.g. "wizard") by storing an empty role instead of
    rejecting the registration (see Use Case #3 Extension 2f finding on
    missing roles; this is the sibling case of an unrecognized-but-present
    role). That empty role then breaks Spring Security's authority parsing
    at login time, so the account can never log in again -- the backend
    returns HTTP 401 with the technical message "A granted authority textual
    representation is required" instead of a user-facing message that
    mentions a role must be selected. This test is expected to FAIL until
    role values are validated at registration time.
    """
    user = unique_user(prefix="login_uc_badrole")
    user["role"] = "not-a-real-role"

    reg_status, reg_body = api_request("POST", "/auth/register", user)
    assert reg_status == 200, reg_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {"username": user["username"], "password": user["password"]},
    )
    assert login_status == 401, login_body
    assert "role" in error_text(login_body).lower()

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


def test_prevents_duplicate_email_registration_and_preserves_original_account():
    """This proves Use Case #2 Main Success Scenario and Postconditions 1, 2, 3:

    A user cannot register a new account using an email address already registered,
    the registration attempt is rejected, the duplicate account is not created,
    and the existing account remains unchanged and accessible.
    """
    # Step 1-6: Initial user registers successfully
    initial_user = unique_user(prefix="orig_user", role="customer")
    reg_status, reg_body = api_request("POST", "/auth/register", initial_user)
    assert reg_status == 200, reg_body

    # Verify initial user can log in and receive token
    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {"username": initial_user["username"], "password": initial_user["password"]},
    )
    assert login_status == 200, login_body
    assert "accessToken" in login_body

    # Step 7-8: Attempt to register a second account with a different username but duplicate email
    duplicate_user = unique_user(prefix="dup_user", role="customer")
    duplicate_user["email"] = initial_user["email"]

    dup_status, dup_body = api_request("POST", "/auth/register", duplicate_user)
    # Registration should be rejected with client error (HTTP 400)
    assert dup_status == 400, dup_body

    # Postcondition 1: The new account with the duplicate email was not created
    dup_login_status, dup_login_body = api_request(
        "POST",
        "/auth/login",
        {"username": duplicate_user["username"], "password": duplicate_user["password"]},
    )
    assert dup_login_status in {400, 401, 403, 404}, (
        f"Duplicate user should not be able to log in: {dup_login_body}"
    )

    # Postcondition 2: The original account with that email remains intact and functional
    orig_login_status, orig_login_body = api_request(
        "POST",
        "/auth/login",
        {"username": initial_user["username"], "password": initial_user["password"]},
    )
    assert orig_login_status == 200, orig_login_body
    assert "accessToken" in orig_login_body


def test_rejects_duplicate_username_registration():
    """This proves Use Case #2 Extension 2a:

    Registration is rejected when a user enters a username that is already taken.
    """
    first_user = unique_user(prefix="taken_uname", role="customer")
    first_status, first_body = api_request("POST", "/auth/register", first_user)
    assert first_status == 200, first_body

    # Second user tries to use same username with different email
    second_user = unique_user(prefix="diff_email", role="customer")
    second_user["username"] = first_user["username"]

    second_status, second_body = api_request("POST", "/auth/register", second_user)
    assert second_status == 400, second_body
    assert second_body.get("error") == "Username already taken"


def test_rejects_registration_with_invalid_password():
    """This proves Use Case #2 Extension 4a:

    Registration is rejected when the user provides an invalid password.
    """
    user = unique_user(prefix="bad_pw_user", role="customer")
    user["password"] = "1"  # Too short

    status, body = api_request("POST", "/auth/register", user)
    assert status >= 400, body


def test_rejects_incomplete_registration_missing_role():
    """This proves Use Case #2 Extension 5a:

    Registration is rejected when required fields such as role are missing.
    """
    user = unique_user(prefix="no_role_user", role="customer")
    del user["role"]

    status, body = api_request("POST", "/auth/register", user)
    assert status >= 400, body


def test_prevents_cross_role_duplicate_email_registration():
    """This proves Use Case #2 duplicate email prevention across different roles:

    An existing Customer email cannot be used to register a new Driver account.
    """
    customer_user = unique_user(prefix="cust_acc", role="customer")
    c_status, c_body = api_request("POST", "/auth/register", customer_user)
    assert c_status == 200, c_body

    driver_user = unique_user(prefix="driver_acc", role="driver")
    driver_user["email"] = customer_user["email"]

    d_status, d_body = api_request("POST", "/auth/register", driver_user)
    assert d_status == 400, d_body


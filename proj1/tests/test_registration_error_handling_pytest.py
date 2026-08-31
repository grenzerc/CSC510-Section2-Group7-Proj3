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


def error_text(body):
    """Registration failures may surface under an 'error' key (validation
    checks in AuthServiceImpl) or a 'message' key (GlobalExceptionHandler),
    depending on which layer rejects the request."""
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


def test_rejects_duplicate_username_with_specific_message():
    """This proves Use Case #3 Extension 2a:

    Registering with a username that is already taken is rejected with a
    client error that specifically calls out the username, not a generic
    failure message.
    """
    first_user = unique_user(prefix="regerr_uname_a")
    first_status, first_body = api_request("POST", "/auth/register", first_user)
    assert first_status == 200, first_body

    second_user = unique_user(prefix="regerr_uname_b")
    second_user["username"] = first_user["username"]

    status, body = api_request("POST", "/auth/register", second_user)
    assert status == 400, body
    assert "username" in error_text(body).lower()
    assert "taken" in error_text(body).lower()


def test_rejects_invalid_password_format_with_specific_message():
    """This proves Use Case #3 Extension 2d:

    Registering with a password that fails the backend's format/length rule
    is rejected with a client error that specifically mentions the password.
    """
    user = unique_user(prefix="regerr_badpw")
    user["password"] = "x"  # below the minimum accepted length

    status, body = api_request("POST", "/auth/register", user)
    assert status == 400, body
    assert "password" in error_text(body).lower()


def test_rejects_duplicate_email_registration_with_client_error():
    """This proves Use Case #3 Extension 2b:

    Registering with an email already tied to another account should be
    rejected with a client error (HTTP 4xx) and a message telling the user
    the email is already in use.

    KNOWN DEFECT (matches Use Case #2's finding in proj1/traceability.md):
    AuthServiceImpl.register never calls userRepository.existsByEmail, so the
    duplicate is only caught by the database's unique constraint on
    users.email. That raised exception falls through to
    GlobalExceptionHandler's generic handler, which returns HTTP 500 with a
    raw SQL error instead of the specific, user-facing message the use case
    calls for. This test is expected to FAIL until that validation is added.
    """
    first_user = unique_user(prefix="regerr_email_a")
    first_status, first_body = api_request("POST", "/auth/register", first_user)
    assert first_status == 200, first_body

    second_user = unique_user(prefix="regerr_email_b")
    second_user["email"] = first_user["email"]

    status, body = api_request("POST", "/auth/register", second_user)
    assert status == 400, body
    assert "email" in error_text(body).lower()


def test_rejects_invalid_email_format_with_specific_message():
    """This proves Use Case #3 Extension 2c:

    Registering with a malformed email address should be rejected with a
    message that specifically explains the email format is invalid.

    KNOWN DEFECT: the email-format branch in AuthServiceImpl.register logs
    and returns the wrong string literal ("Username must be between 3-50
    characters" instead of an email-specific message), so the frontend
    cannot tell the user their *email* was the problem. This test is
    expected to FAIL until that message is corrected.
    """
    user = unique_user(prefix="regerr_bademail")
    user["email"] = "not-an-email"

    status, body = api_request("POST", "/auth/register", user)
    assert status == 400, body
    assert "email" in error_text(body).lower()


def test_rejects_missing_role_with_client_error():
    """This proves Use Case #3 Extension 2f:

    Registering without selecting a role should be rejected with a client
    error and a message telling the user a role must be selected.

    KNOWN DEFECT: AuthServiceImpl has no explicit check for a missing role.
    When "role" is absent, setCorrectRoles calls req.role().toLowerCase() on
    a null value, throwing a NullPointerException that GlobalExceptionHandler
    reports as an HTTP 500 with a raw Java error message rather than the
    "select a role" message the use case calls for. This test is expected to
    FAIL until role validation is added.
    """
    user = unique_user(prefix="regerr_norole")
    del user["role"]

    status, body = api_request("POST", "/auth/register", user)
    assert status == 400, body
    assert "role" in error_text(body).lower()


def test_invalid_registration_does_not_create_account():
    """This proves Use Case #3 Postconditions 1 and 2:

    When registration is rejected (here, for an invalid password), no
    account is created, so logging in with those credentials still fails.
    """
    user = unique_user(prefix="regerr_noaccount")
    user["password"] = "x"

    reg_status, reg_body = api_request("POST", "/auth/register", user)
    assert reg_status == 400, reg_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {"username": user["username"], "password": user["password"]},
    )
    assert login_status in {400, 401, 403, 404}, (
        f"No account should exist after a rejected registration: {login_body}"
    )


def test_user_can_correct_and_resubmit_after_registration_error():
    """This proves Use Case #3 main success scenario step 7 and
    Postcondition 4:

    After a registration attempt fails (duplicate username), the user stays
    able to correct the offending field and resubmit successfully, ending up
    with a working account.
    """
    taken_user = unique_user(prefix="regerr_retry_taken")
    taken_status, taken_body = api_request("POST", "/auth/register", taken_user)
    assert taken_status == 200, taken_body

    retry_user = unique_user(prefix="regerr_retry_new")
    retry_user["username"] = taken_user["username"]

    failed_status, failed_body = api_request("POST", "/auth/register", retry_user)
    assert failed_status == 400, failed_body

    # User corrects the username (the field the error message pointed to)
    # and resubmits with everything else unchanged.
    retry_user["username"] = unique_user(prefix="regerr_retry_fixed")["username"]

    fixed_status, fixed_body = api_request("POST", "/auth/register", retry_user)
    assert fixed_status == 200, fixed_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {"username": retry_user["username"], "password": retry_user["password"]},
    )
    assert login_status == 200, login_body
    assert "accessToken" in login_body

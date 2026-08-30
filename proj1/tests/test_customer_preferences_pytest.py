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


def unique_driver(prefix="driver"):
    timestamp_letters = base26_letters(int(time.time()))
    pid_letters = base26_letters(os.getpid())
    run_id = f"{timestamp_letters}_{pid_letters}"
    username = f"{prefix}_{run_id}"
    return {
        "username": username,
        "email": f"{username}@example.com",
        "password": "driverpass123",
        "role": "driver",
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


def create_and_login_customer(prefix):
    customer = unique_driver(prefix)
    customer["role"] = "customer"

    register_status, register_body = api_request(
        "POST",
        "/auth/register",
        customer,
    )
    assert register_status == 200, register_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {
            "username": customer["username"],
            "password": customer["password"],
        },
    )
    assert login_status == 200, login_body
    assert login_body["accessToken"]

    return customer, login_body["accessToken"]


def test_customer_can_update_food_preferences():
    """This proves the main success scenario for updating food preferences."""
    customer, token = create_and_login_customer("preferences_customer")

    update_status, update_body = api_request(
        "PUT",
        "/api/users/me/preferences",
        {
            "costPreference": "moderate",
            "dietaryRestrictions": "MILK, GLUTEN",
        },
        token=token,
    )

    assert update_status == 200, update_body
    assert update_body["username"] == customer["username"]
    assert update_body["costPreference"] == "moderate"
    assert update_body["dietaryRestrictions"] == "MILK, GLUTEN"


def test_updated_food_preferences_are_returned_in_customer_profile():
    """This proves saved preferences persist and can be retrieved later."""
    customer, token = create_and_login_customer("persistent_preferences_customer")

    update_status, update_body = api_request(
        "PUT",
        "/api/users/me/preferences",
        {
            "costPreference": "premium",
            "dietaryRestrictions": "SHELLFISH, PEANUTS",
        },
        token=token,
    )
    assert update_status == 200, update_body

    profile_status, profile_body = api_request(
        "GET",
        "/api/users/me",
        token=token,
    )

    assert profile_status == 200, profile_body
    assert profile_body["username"] == customer["username"]
    assert profile_body["costPreference"] == "premium"
    assert profile_body["dietaryRestrictions"] == "SHELLFISH, PEANUTS"


def test_customer_can_save_preferences_without_dietary_restrictions():
    """This proves customers can save a budget without selecting restrictions."""
    customer, token = create_and_login_customer("no_restrictions_customer")

    update_status, update_body = api_request(
        "PUT",
        "/api/users/me/preferences",
        {
            "costPreference": "budget",
            "dietaryRestrictions": "",
        },
        token=token,
    )

    assert update_status == 200, update_body
    assert update_body["username"] == customer["username"]
    assert update_body["costPreference"] == "budget"
    assert update_body["dietaryRestrictions"] == ""



def test_rejects_unsupported_cost_preference():
    """This checks whether the backend rejects a budget value not offered by the program."""
    customer, token = create_and_login_customer("invalid_budget_customer")

    update_status, update_body = api_request(
        "PUT",
        "/api/users/me/preferences",
        {
            "costPreference": "one-million-dollars",
            "dietaryRestrictions": "MILK",
        },
        token=token,
    )

    assert update_status == 400, update_body
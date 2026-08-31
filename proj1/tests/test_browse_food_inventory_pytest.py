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


def test_authenticated_customer_can_browse_food_inventory():
    """This proves the main scenario: an authenticated user can retrieve the food inventory."""
    customer, token = create_and_login_customer("browse_inventory_customer")

    foods_status, foods_body = api_request(
        "GET",
        "/api/foods",
        token=token,
    )

    assert foods_status == 200, foods_body
    assert isinstance(foods_body, list), foods_body
    assert len(foods_body) > 0, foods_body


def test_inventory_foods_contain_displayed_information():
    """This proves that returned foods contain the information used by the inventory cards."""
    customer, token = create_and_login_customer("inventory_details_customer")

    foods_status, foods_body = api_request(
        "GET",
        "/api/foods",
        token=token,
    )

    assert foods_status == 200, foods_body
    assert isinstance(foods_body, list), foods_body
    assert len(foods_body) > 0, foods_body

    required_fields = {
        "id",
        "foodName",
        "amount",
        "price",
        "rating",
        "numberOfRatings",
        "allergies",
    }

    for food in foods_body:
        assert required_fields.issubset(food.keys()), food
        assert isinstance(food["foodName"], str), food
        assert food["foodName"].strip() != "", food
        assert isinstance(food["amount"], int), food
        assert isinstance(food["price"], int), food


def test_rejects_unauthenticated_food_inventory_request():
    """This proves extension 1a: the backend rejects inventory requests without authentication."""
    foods_status, foods_body = api_request(
        "GET",
        "/api/foods",
    )

    assert foods_status in (401, 403), foods_body


def test_browsing_food_inventory_does_not_change_inventory():
    """This proves the read-only postcondition: browsing does not modify food records."""
    customer, token = create_and_login_customer("readonly_inventory_customer")

    first_status, first_body = api_request(
        "GET",
        "/api/foods",
        token=token,
    )
    second_status, second_body = api_request(
        "GET",
        "/api/foods",
        token=token,
    )

    assert first_status == 200, first_body
    assert second_status == 200, second_body
    assert first_body == second_body
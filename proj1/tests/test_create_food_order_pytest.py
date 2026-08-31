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


def get_in_stock_food(token):
    """Return one food that currently has at least one unit in stock."""
    foods_status, foods_body = api_request(
        "GET",
        "/api/foods",
        token=token,
    )

    assert foods_status == 200, foods_body
    assert isinstance(foods_body, list), foods_body

    in_stock_foods = [
        food for food in foods_body
        if isinstance(food.get("amount"), int) and food["amount"] > 0
    ]

    assert in_stock_foods, "The test database has no in-stock foods."
    return in_stock_foods[0]


def build_order_payload(food, quantity=1, name="Pytest Food Order"):
    """Build the same order structure submitted by CreateOrder.js."""
    subtotal = food["price"] * quantity
    delivery_cost = round(subtotal * 0.30, 2)
    total_cost = round(subtotal + delivery_cost, 2)

    return {
        "name": name,
        "foods": [
            {"id": food["id"]}
            for _ in range(quantity)
        ],
        "isFulfilled": False,
        "cost": total_cost,
        "status": "Placed",
        "deliveryCost": delivery_cost,
    }

def test_authenticated_customer_can_create_food_order():
    """This proves the main scenario: a customer can create an order containing an in-stock food."""
    customer, token = create_and_login_customer("create_order_customer")
    food = get_in_stock_food(token)
    order_payload = build_order_payload(
        food,
        quantity=1,
        name="Main Scenario Order",
    )

    order_status, order_body = api_request(
        "POST",
        "/api/orders",
        order_payload,
        token=token,
    )

    assert order_status == 200, order_body
    assert order_body["id"] is not None, order_body
    assert order_body["name"] == "Main Scenario Order", order_body
    assert order_body["isFulfilled"] is False, order_body
    assert order_body["status"] == "Placed", order_body


def test_created_order_appears_in_customer_orders():
    """This proves the success postcondition: the saved order belongs to the customer."""
    customer, token = create_and_login_customer("persisted_order_customer")
    food = get_in_stock_food(token)
    order_payload = build_order_payload(
        food,
        quantity=1,
        name="Persisted Customer Order",
    )

    create_status, create_body = api_request(
        "POST",
        "/api/orders",
        order_payload,
        token=token,
    )

    assert create_status == 200, create_body
    created_order_id = create_body["id"]

    orders_status, orders_body = api_request(
        "GET",
        "/api/orders/my-orders",
        token=token,
    )

    assert orders_status == 200, orders_body
    assert isinstance(orders_body, list), orders_body
    assert any(
        order["id"] == created_order_id
        for order in orders_body
    ), orders_body


def test_rejects_order_without_food():
    """This checks whether the backend rejects an order containing no food."""
    customer, token = create_and_login_customer("empty_order_customer")

    empty_order = {
        "name": "Empty Food Order",
        "foods": [],
        "isFulfilled": False,
        "cost": 0,
        "status": "Placed",
        "deliveryCost": 0,
    }

    order_status, order_body = api_request(
        "POST",
        "/api/orders",
        empty_order,
        token=token,
    )

    assert order_status == 400, order_body


def test_rejects_order_quantity_above_available_stock():
    """This checks whether the backend rejects a quantity greater than current stock."""
    customer, token = create_and_login_customer("overstock_order_customer")
    food = get_in_stock_food(token)
    unavailable_quantity = food["amount"] + 1

    order_payload = build_order_payload(
        food,
        quantity=unavailable_quantity,
        name="Excess Stock Order",
    )

    order_status, order_body = api_request(
        "POST",
        "/api/orders",
        order_payload,
        token=token,
    )

    assert order_status == 400, order_body
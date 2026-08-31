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

def test_customer_can_view_personal_orders():
    """This proves the main scenario: a customer can retrieve an order associated with their account."""
    customer, token = create_and_login_customer("view_orders_customer")
    food = get_in_stock_food(token)

    order_payload = build_order_payload(
        food,
        quantity=1,
        name="Visible Personal Order",
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


def test_personal_orders_do_not_include_another_customers_order():
    """This proves account isolation: one customer cannot see another customer's order."""
    first_customer, first_token = create_and_login_customer(
        "private_order_owner"
    )
    food = get_in_stock_food(first_token)

    order_payload = build_order_payload(
        food,
        quantity=1,
        name="Private Customer Order",
    )

    create_status, create_body = api_request(
        "POST",
        "/api/orders",
        order_payload,
        token=first_token,
    )

    assert create_status == 200, create_body
    private_order_id = create_body["id"]

    second_customer, second_token = create_and_login_customer(
        "unrelated_customer"
    )

    second_status, second_body = api_request(
        "GET",
        "/api/orders/my-orders",
        token=second_token,
    )

    assert second_status == 200, second_body
    assert isinstance(second_body, list), second_body
    assert all(
        order["id"] != private_order_id
        for order in second_body
    ), second_body


def test_new_customer_receives_empty_personal_order_list():
    """This proves the empty-state data condition: a new customer has no personal orders."""
    customer, token = create_and_login_customer("empty_orders_customer")

    orders_status, orders_body = api_request(
        "GET",
        "/api/orders/my-orders",
        token=token,
    )

    assert orders_status == 200, orders_body
    assert orders_body == [], orders_body


def test_personal_order_details_preserve_repeated_food_entries():
    """This proves that quantities are returned as repeated food entries for display."""
    customer, token = create_and_login_customer("order_details_customer")
    food = get_in_stock_food(token)

    order_payload = build_order_payload(
        food,
        quantity=2,
        name="Repeated Food Details",
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

    matching_order = next(
        (
            order for order in orders_body
            if order["id"] == created_order_id
        ),
        None,
    )

    assert matching_order is not None, orders_body
    assert matching_order["name"] == "Repeated Food Details", matching_order
    assert matching_order["isFulfilled"] is False, matching_order
    assert len(matching_order["foods"]) == 2, matching_order
    assert all(
        returned_food["id"] == food["id"]
        for returned_food in matching_order["foods"]
    ), matching_order
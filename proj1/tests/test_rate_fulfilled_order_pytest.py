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


def create_and_login_driver(prefix):
    """Register and authenticate a unique driver."""
    driver = unique_driver(prefix)
    driver["role"] = "driver"

    register_status, register_body = api_request(
        "POST",
        "/auth/register",
        driver,
    )
    assert register_status == 200, register_body

    login_status, login_body = api_request(
        "POST",
        "/auth/login",
        {
            "username": driver["username"],
            "password": driver["password"],
        },
    )
    assert login_status == 200, login_body

    token = login_body.get("accessToken")
    assert token, login_body

    return driver, token

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


def create_order(customer_token, food, name):
    """Create one pending order containing one unit of the supplied food."""
    order_payload = build_order_payload(
        food,
        quantity=1,
        name=name,
    )

    order_status, order_body = api_request(
        "POST",
        "/api/orders",
        order_payload,
        token=customer_token,
    )

    assert order_status == 200, order_body
    return order_body


def mark_order_fulfilled(order_id, driver, driver_token):
    """Move an order through Picked Up and Delivered using a driver account."""
    pickup_status, pickup_body = api_request(
        "POST",
        f"/api/orders/{order_id}",
        {
            "status": "Picked Up",
            "username": driver["username"],
        },
        token=driver_token,
    )
    assert pickup_status == 200, pickup_body

    delivery_status, delivery_body = api_request(
        "POST",
        f"/api/orders/{order_id}",
        {
            "status": "Delivered",
            "username": driver["username"],
        },
        token=driver_token,
    )
    assert delivery_status == 200, delivery_body

    return delivery_body

def test_customer_can_rate_food_from_fulfilled_order():
    """This proves the main scenario: the order owner can rate food after fulfillment."""
    customer, customer_token = create_and_login_customer(
        "successful_rating_customer"
    )
    food = get_in_stock_food(customer_token)
    order = create_order(
        customer_token,
        food,
        "Successful Rating Order",
    )

    driver, driver_token = create_and_login_driver(
        "successful_rating_driver"
    )
    fulfilled_order = mark_order_fulfilled(
        order["id"],
        driver,
        driver_token,
    )

    assert fulfilled_order["isFulfilled"] is True, fulfilled_order

    rating_status, rating_body = api_request(
        "POST",
        f"/api/foods/orders/{order['id']}/{food['id']}/rate?rating=4.5",
        token=customer_token,
    )

    assert rating_status == 200, rating_body
    assert rating_body["id"] == food["id"], rating_body
    assert rating_body["numberOfRatings"] == food["numberOfRatings"] + 1, rating_body

    orders_status, orders_body = api_request(
        "GET",
        "/api/orders/my-orders",
        token=customer_token,
    )

    assert orders_status == 200, orders_body

    rated_order = next(
        item for item in orders_body
        if item["id"] == order["id"]
    )

    assert food["id"] in rated_order["ratedFoodIds"], rated_order


def test_rejects_duplicate_rating_for_same_food_and_order():
    """This proves the duplicate-rating extension."""
    customer, customer_token = create_and_login_customer(
        "duplicate_rating_customer"
    )
    food = get_in_stock_food(customer_token)
    order = create_order(
        customer_token,
        food,
        "Duplicate Rating Order",
    )

    driver, driver_token = create_and_login_driver(
        "duplicate_rating_driver"
    )
    mark_order_fulfilled(order["id"], driver, driver_token)

    first_status, first_body = api_request(
        "POST",
        f"/api/foods/orders/{order['id']}/{food['id']}/rate?rating=4",
        token=customer_token,
    )
    assert first_status == 200, first_body

    second_status, second_body = api_request(
        "POST",
        f"/api/foods/orders/{order['id']}/{food['id']}/rate?rating=3",
        token=customer_token,
    )

    assert second_status == 409, second_body


def test_rejects_rating_food_from_unfulfilled_order():
    """This proves that pending orders cannot be rated by bypassing the frontend."""
    customer, customer_token = create_and_login_customer(
        "pending_rating_customer"
    )
    food = get_in_stock_food(customer_token)
    order = create_order(
        customer_token,
        food,
        "Pending Rating Order",
    )

    rating_status, rating_body = api_request(
        "POST",
        f"/api/foods/orders/{order['id']}/{food['id']}/rate?rating=4",
        token=customer_token,
    )

    assert rating_status == 409, rating_body


def test_rejects_rating_another_customers_order():
    """This checks whether the backend prevents cross-account order rating."""
    owner, owner_token = create_and_login_customer(
        "rating_order_owner"
    )
    food = get_in_stock_food(owner_token)
    order = create_order(
        owner_token,
        food,
        "Private Rating Order",
    )

    driver, driver_token = create_and_login_driver(
        "private_rating_driver"
    )
    mark_order_fulfilled(order["id"], driver, driver_token)

    unrelated_customer, unrelated_token = create_and_login_customer(
        "unauthorized_rating_customer"
    )

    rating_status, rating_body = api_request(
        "POST",
        f"/api/foods/orders/{order['id']}/{food['id']}/rate?rating=1",
        token=unrelated_token,
    )

    assert rating_status in (403, 404), rating_body
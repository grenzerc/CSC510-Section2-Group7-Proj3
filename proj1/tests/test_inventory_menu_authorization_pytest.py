"""Use Case #12 -- Manage the food inventory.

Most of this use case is about who is allowed to write, so most of these tests
are authorization tests. They create and delete their own menu items rather
than touching whatever is already seeded.
"""

import pytest

from api_helpers import (
    api_request,
    admin_token,
    register_and_login,
    require_backend,
    unique_name,
)


@pytest.fixture(scope="module", autouse=True)
def backend():
    require_backend()


@pytest.fixture(scope="module")
def admin():
    return admin_token()


@pytest.fixture
def menu_item(admin):
    """Adds a food, yields it, and removes it again afterwards.

    We share one database while testing, so leaving test_food_* rows behind
    would show up on everyone else's Inventory page.
    """
    created = []

    def add(price=12, amount=5, allergies=None):
        food = {
            "foodName": unique_name("test_food"),
            "amount": amount,
            "price": price,
            "allergies": allergies or [],
        }
        status, body = api_request("POST", "/api/foods", food, token=admin)
        assert status == 200, body
        created.append(body)
        return body

    yield add

    for food in created:
        api_request("DELETE", f"/api/foods/{food['id']}", token=admin)


def test_staff_can_read_the_inventory():
    """This proves step 2 of the main scenario."""
    _, staff = register_and_login("staff", "stock_reader")

    status, body = api_request("GET", "/api/inventory", token=staff)

    assert status == 200, body
    assert "foods" in body


def test_the_inventory_cannot_be_read_without_logging_in():
    """This proves extension 2a."""
    status, body = api_request("GET", "/api/inventory")

    assert status == 401, body


def test_a_customer_cannot_rewrite_the_inventory(admin):
    """This proves extension 4a: stock levels are not a customer's to set.

    Expected to fail today. InventoryController guards both endpoints with
    hasAnyRole('ADMIN', 'STAFF', 'CUSTOMER'), so a customer is allowed to POST.
    We read the current inventory as admin and post it back unchanged, so a
    pass or a fail leaves the data alone either way.
    """
    read_status, inventory = api_request("GET", "/api/inventory", token=admin)
    assert read_status == 200, inventory

    _, customer = register_and_login("customer", "stock_meddler")
    status, body = api_request("POST", "/api/inventory", inventory, token=customer)

    assert status == 403, f"a customer was allowed to write the inventory: {status} {body}"


def test_a_driver_cannot_add_a_menu_item():
    """This proves extension 4b: menu changes belong to staff.

    Expected to fail today. FoodController carries no @PreAuthorize at all, so
    every authenticated account can create food.
    """
    _, driver = register_and_login("driver", "menu_meddler")
    food = {
        "foodName": unique_name("driver_food"),
        "amount": 1,
        "price": 5,
        "allergies": [],
    }

    status, body = api_request("POST", "/api/foods", food, token=driver)

    if status == 200:
        # clean up after the bug so the menu is not left polluted
        api_request("DELETE", f"/api/foods/{body['id']}", token=admin_token())

    assert status == 403, f"a driver was allowed to add a menu item: {status} {body}"


def test_a_customer_cannot_delete_a_menu_item(menu_item):
    """This proves extension 4b for deletion, which is the destructive half.

    Expected to fail today, and worse than expected. There is no authorization
    check, so the request is not stopped at 403 -- it reaches the database and
    the food is still referenced by the singleton Inventory's food list, which
    trips a foreign key constraint. FoodController.deleteFood() only catches
    IllegalStateException (foods in unfulfilled orders); it does not catch this,
    so the raw MySQL constraint message is returned to the client as an
    unhandled HTTP 500. This is not just a missing authorization check -- it is
    an information disclosure: any caller who triggers it, including an admin,
    sees internal SQL and schema details in the response body.
    """
    food = menu_item()
    _, customer = register_and_login("customer", "menu_deleter")

    status, body = api_request("DELETE", f"/api/foods/{food['id']}", token=customer)

    assert status == 403, f"a customer deleted a menu item: {status} {body}"


def test_rejects_a_negative_price(admin, menu_item):
    """This proves extension 4c."""
    food = menu_item(price=8)
    update = {
        "foodName": food["foodName"],
        "amount": food["amount"],
        "price": -1,
        "allergies": [],
    }

    status, body = api_request("POST", "/api/foods/updateFood", update, token=admin)

    assert status == 400, body


def test_rejects_a_duplicate_food_name(admin, menu_item):
    """This proves extension 4e."""
    food = menu_item()
    duplicate = {
        "foodName": food["foodName"],
        "amount": 3,
        "price": 9,
        "allergies": [],
    }

    status, body = api_request("POST", "/api/foods", duplicate, token=admin)

    assert status == 409, body

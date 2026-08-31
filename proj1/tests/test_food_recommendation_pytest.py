"""Use Case #14 -- Get a food recommendation.

Worth knowing before reading this file: FoodSeer does not have a recommendation
endpoint. Recommendations.js pulls the whole menu and filters it in the browser.
So there are two kinds of test here -- ones that hit the API to show the server
does no filtering at all, and ones that run the browser's filter over real menu
data to show what it gets wrong.

The port of that filter lives in preference_filter() below. If
food-seer-frontend/src/pages/Recommendations.js changes, this has to change too.
"""

import pytest

from api_helpers import (
    api_request,
    admin_token,
    register_and_login,
    require_backend,
    unique_name,
)

BUDGET_CAPS = {"budget": 10, "moderate": 20, "premium": 35}


def preference_filter(food, cost_preference, dietary_restrictions):
    """Port of filterFoodsByPreferences() from Recommendations.js.

    Deliberately a literal translation, including the parts that are wrong --
    the point is to test what the app actually does, not what it should do.
    """
    cap = BUDGET_CAPS.get((cost_preference or "").lower())
    if cap is not None and food["price"] > cap:
        return False

    allergens = [a.lower() for a in (food.get("allergies") or [])]
    if not allergens:
        return True

    restrictions = [
        r.strip().lower()
        for r in (dietary_restrictions or "").split(",")
        if r.strip()
    ]

    # The JS compares with ===, so this is an exact match on purpose.
    return not any(restriction in allergens for restriction in restrictions)


@pytest.fixture(scope="module", autouse=True)
def backend():
    require_backend()


@pytest.fixture(scope="module")
def admin():
    return admin_token()


@pytest.fixture
def menu_item(admin):
    created = []

    def add(price=12, allergies=None):
        food = {
            "foodName": unique_name("rec_food"),
            "amount": 5,
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


def set_preferences(token, cost, restrictions):
    status, body = api_request(
        "PUT",
        "/api/users/me/preferences",
        {"costPreference": cost, "dietaryRestrictions": restrictions},
        token=token,
    )
    assert status == 200, body
    return body


def test_a_customer_can_save_a_budget_and_a_restriction():
    """This proves the preconditions hold -- preferences are stored and read back."""
    _, customer = register_and_login("customer", "picky")

    saved = set_preferences(customer, "budget", "peanut")

    assert saved["costPreference"] == "budget"
    assert saved["dietaryRestrictions"] == "peanut"


def test_an_exactly_worded_restriction_hides_the_food(menu_item):
    """This proves step 4 works when the wording happens to line up."""
    food = menu_item(price=8, allergies=["peanut"])

    assert preference_filter(food, "no-limit", "peanut") is False


def test_a_plural_restriction_still_hides_the_food(menu_item):
    """This proves extension 4a, and it is the one that matters.

    Expected to fail. The filter compares allergen and restriction with ===,
    so a customer who wrote "peanuts" is shown a dish whose allergen is
    recorded as "peanut". The app tells them it is safe to eat.
    """
    food = menu_item(price=8, allergies=["peanut"])

    assert preference_filter(food, "no-limit", "peanuts") is False, (
        f"{food['foodName']} contains peanut but survived a 'peanuts' restriction"
    )


def test_a_broader_restriction_still_hides_the_food(menu_item):
    """This proves extension 4a again with a category rather than a plural.

    Expected to fail. "nuts" does not equal "tree nuts".
    """
    food = menu_item(price=8, allergies=["tree nuts"])

    assert preference_filter(food, "no-limit", "nuts") is False, (
        f"{food['foodName']} contains tree nuts but survived a 'nuts' restriction"
    )


def test_premium_customers_can_see_the_whole_menu(menu_item):
    """This proves extension 3b.

    Expected to fail. "premium" is capped at 35, so the customer who picked the
    most permissive tier is the only one who cannot see a $40 dish.
    """
    expensive = menu_item(price=40)

    assert preference_filter(expensive, "premium", "") is True, (
        "the premium tier hid a dish it should have shown"
    )


def test_the_food_api_applies_no_preferences_of_its_own(menu_item):
    """This proves extension 5a: filtering is presentation only.

    Expected to fail. The customer says they cannot eat peanuts, and
    GET /api/foods hands back the peanut dish anyway, because no filtering
    happens on the server at all.
    """
    food = menu_item(price=8, allergies=["peanut"])
    _, customer = register_and_login("customer", "allergic")
    set_preferences(customer, "budget", "peanut")

    status, menu = api_request("GET", "/api/foods", token=customer)
    assert status == 200, menu

    returned = [item["foodName"] for item in menu]
    assert food["foodName"] not in returned, (
        "the API returned a dish the customer is allergic to -- "
        "any client that skips the browser filter shows it"
    )

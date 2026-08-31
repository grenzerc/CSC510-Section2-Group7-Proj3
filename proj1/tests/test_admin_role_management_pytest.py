"""Use Case #11 -- Change a user's role.

Needs the backend running and the seeded admin account (admin / admin123).
"""

import pytest

from api_helpers import (
    api_request,
    admin_token,
    find_user_id,
    new_account,
    register_and_login,
    require_backend,
)


@pytest.fixture(scope="module", autouse=True)
def backend():
    require_backend()


@pytest.fixture(scope="module")
def admin():
    return admin_token()


def test_admin_can_promote_a_customer_to_staff(admin):
    """This proves the main success scenario."""
    account, _ = register_and_login("customer", "promote_me")
    user_id = find_user_id(admin, account["username"])

    status, body = api_request(
        "PUT", f"/api/users/{user_id}/role", {"role": "ROLE_STAFF"}, token=admin
    )

    assert status == 200, body
    assert body["role"] == "ROLE_STAFF"


def test_a_customer_cannot_list_every_user():
    """This proves extension 2a: the user list is admin-only."""
    _, customer = register_and_login("customer", "nosy")

    status, body = api_request("GET", "/api/users", token=customer)

    assert status == 403, body


def test_changing_the_role_of_a_user_that_does_not_exist_is_not_found(admin):
    """This proves extension 5a: an unknown id is rejected rather than silently ignored."""
    status, body = api_request(
        "PUT", "/api/users/99999999/role", {"role": "ROLE_STAFF"}, token=admin
    )

    assert status == 404, body


def test_rejects_a_role_that_is_not_a_real_role(admin):
    """This proves extension 5b: garbage roles should not be stored.

    Expected to fail today. UserServiceImpl.updateUserRole hands the string
    straight to setRole() without checking it against either Roles class, so
    the backend answers 200 and persists whatever it was given.
    """
    account, _ = register_and_login("customer", "wizard")
    user_id = find_user_id(admin, account["username"])

    status, body = api_request(
        "PUT", f"/api/users/{user_id}/role", {"role": "ROLE_WIZARD"}, token=admin
    )

    assert status == 400, f"backend accepted an invented role: {status} {body}"


def test_rejects_an_empty_role(admin):
    """This proves extension 5b for the empty string, which leaves an account able
    to log in but authorized for nothing."""
    account, _ = register_and_login("customer", "blank_role")
    user_id = find_user_id(admin, account["username"])

    status, body = api_request(
        "PUT", f"/api/users/{user_id}/role", {"role": ""}, token=admin
    )

    assert status == 400, f"backend accepted an empty role: {status} {body}"


def test_registering_with_an_unknown_role_is_rejected():
    """This proves extension 4a from the other direction.

    setCorrectRoles() returns "" for anything that is not driver/customer/staff,
    so registering as "admin" quietly creates an account with no role at all.
    """
    account = new_account("admin", "fake_admin")
    status, body = api_request("POST", "/auth/register", account)

    assert status == 400, f"registration accepted an unknown role: {status} {body}"


@pytest.mark.skip(
    reason="would demote the shared admin and lock the whole team out of /api/users"
)
def test_the_last_admin_cannot_be_demoted(admin):
    """This proves extension 5c. Written up but deliberately not run -- see test-plan.md."""
    user_id = find_user_id(admin, "admin")

    status, _ = api_request(
        "PUT", f"/api/users/{user_id}/role", {"role": "ROLE_CUSTOMER"}, token=admin
    )

    assert status == 400

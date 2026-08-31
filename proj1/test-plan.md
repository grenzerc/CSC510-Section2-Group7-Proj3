# Project 1 Test Plan

## Use Case #1: Driver Registration and Dashboard Access

Test file:
- `proj1/tests/test_driver_registration_dashboard_pytest.py`

Runner:
- `proj1/tests/run_driver_registration_dashboard_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. Start the frontend:
   `cd food-seer-frontend`
   `npm start`
3. From the repository root, run:
   `proj1/tests/run_driver_registration_dashboard_pytest.sh`

Test Cases:
- Main success scenario: registers a new driver, logs in, verifies `ROLE_DRIVER`, and verifies driver statistics can be loaded.
- Extension 3a: sends incomplete registration information and verifies the system rejects it.
- Extension 5a: registers a second account with an existing email and expects a clean validation failure.
- Extension 7a: logs in with invalid credentials and verifies authentication is rejected.

Known Result:
- The main driver registration and dashboard access path passes.
- Extension 5a currently fails because the backend returns HTTP 500 from a database uniqueness error instead of a clean HTTP 400 validation response for duplicate email addresses.

## Use Case #11: Administrative Role Management

Test file:
- `proj1/tests/test_admin_role_management_pytest.py`

Runner:
- `proj1/tests/run_admin_role_management_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. From the repository root, run:
   `proj1/tests/run_admin_role_management_pytest.sh`
3. Requires the seeded `admin` / `admin123` account (created by `DataInitializer`).

Test Cases:
- Main success scenario: admin promotes a customer to `ROLE_STAFF` and the change is returned.
- Extension 2a: a customer requests the full user list and is rejected.
- Extension 5a: an admin changes the role of a user id that does not exist.
- Extension 5b: an admin submits a role that is not a real role (`ROLE_WIZARD`).
- Extension 5b (empty case): an admin submits an empty string as the role.
- Extension 4a: a user registers with a role string outside driver/customer/staff.
- Extension 5c: the last remaining admin is demoted. Written but skipped on purpose
  -- there is only one seeded admin account and every teammate shares it, so running
  this would lock the whole team out of `/api/users` with no way back in.

Known Result:
- The main promotion path passes, and the endpoint is correctly admin-only.
- Extension 5a passes: an unknown user id returns 404.
- Extension 5b fails on both cases. `UserServiceImpl.updateUserRole` calls
  `user.setRole(role)` with no validation against either `Roles` class, so the
  backend returns HTTP 200 and persists `ROLE_WIZARD` and `""` alike.
- Extension 4a fails the same way from the registration side: `setCorrectRoles()`
  returns `""` for any role string other than driver/customer/staff, and
  `AuthController.register` stores the account anyway with HTTP 200 and the
  message "Registered". The account exists, can log in, and is authorized for
  nothing.

## Use Case #12: Inventory and Menu Management

Test file:
- `proj1/tests/test_inventory_menu_authorization_pytest.py`

Runner:
- `proj1/tests/run_inventory_menu_authorization_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. From the repository root, run:
   `proj1/tests/run_inventory_menu_authorization_pytest.sh`
3. Requires the seeded `admin` / `admin123` account.

Test Cases:
- Main success scenario: a staff account reads the inventory.
- Extension 2a: the inventory cannot be read without logging in.
- Extension 4a: a customer attempts to overwrite the inventory.
- Extension 4b: a driver attempts to add a menu item; a customer attempts to
  delete one.
- Extension 4c: a negative price is rejected.
- Extension 4e: a duplicate food name is rejected.

Known Result:
- The read path and its 401-when-unauthenticated case both pass.
- Price and duplicate-name validation on writes both pass.
- Extension 4a fails: `InventoryController` guards both `GET` and `POST` with
  `hasAnyRole('ADMIN', 'STAFF', 'CUSTOMER')`, so a customer's POST to
  `/api/inventory` returns 200 and is accepted as a valid write.
- Extension 4b fails for creation the way expected: `FoodController` has no
  `@PreAuthorize` on `POST /api/foods` at all, so a driver account creates a
  menu item and gets back 200.
- Extension 4b fails for deletion worse than expected. There is no
  authorization check here either, but the request does not even reach a clean
  403 -- it reaches the database, where the food is still referenced by the
  singleton Inventory's food list and trips a MySQL foreign key constraint.
  `FoodController.deleteFood()` only catches `IllegalStateException` (for foods
  in unfulfilled orders); it does not catch this, so the raw constraint message
  ("Cannot delete or update a parent row: a foreign key constraint fails...")
  is returned to the client as an unhandled HTTP 500. This is an information
  disclosure on top of the missing authorization check -- any caller who
  triggers it, admin included, would see internal SQL and schema details.

## Use Case #13: Driver Delivery Statistics

Test file:
- `proj1/tests/test_driver_stats_access_pytest.py`

Runner:
- `proj1/tests/run_driver_stats_access_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. From the repository root, run:
   `proj1/tests/run_driver_stats_access_pytest.sh`

Test Cases:
- Main success scenario: a driver reads their own statistics.
- Extension 2a: statistics are requested with no login at all.
- Extension 2b: one driver requests another driver's statistics.
- Extension 2b (non-driver case): a customer requests a driver's statistics.
- Extension 2c: an unknown username is requested.

Known Result:
- The main path passes: a driver reads their own zeroed-out statistics right
  after registration.
- Every other case fails, and all for the same root cause.
  `SpringSecurityConfig` calls `permitAll()` on every `GET` under
  `/api/driverStats/**`, and `DriverStatsController` has no `@PreAuthorize` at
  all -- the annotation is imported in that file and never applied. The
  endpoint also never compares the `username` query parameter against the
  authenticated caller.
- Extension 2a fails: statistics are served with zero credentials (200,
  not 401).
- Extension 2b fails both ways: a second driver reads the first driver's
  earnings (200, not 403), and a customer account reads a driver's earnings
  the same way (200, not 403).
- Extension 2c fails: an unknown username returns 200 with an empty body
  instead of 404, so a caller cannot tell "no such driver" apart from
  "a real driver with nothing delivered yet."

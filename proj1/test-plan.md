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

## Use Case #14: Food Recommendation

Test file:
- `proj1/tests/test_food_recommendation_pytest.py`

Runner:
- `proj1/tests/run_food_recommendation_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. From the repository root, run:
   `proj1/tests/run_food_recommendation_pytest.sh`

Note on approach:
- There is no recommendation endpoint. `Recommendations.js` pulls the full menu
  from `GET /api/foods` and filters it client-side in
  `filterFoodsByPreferences()`. `preference_filter()` in the test file is a
  direct port of that function, wrong parts included, so these tests exercise
  what the app actually does rather than what a recommendation feature should do.

Test Cases:
- Precondition check: a customer saves a budget tier and a dietary restriction.
- Extension 4a (exact match): an allergen worded exactly like the restriction
  hides the food.
- Extension 4a (plural): a restriction of "peanuts" against an allergen of
  "peanut".
- Extension 4a (category): a restriction of "nuts" against an allergen of
  "tree nuts".
- Extension 3b: a customer on the "premium" tier views a $40 dish.
- Extension 5a: a customer with a saved peanut restriction calls
  `GET /api/foods` directly.

Known Result:
- Preferences save and read back correctly, and an exact-wording match does
  hide the food -- the filter is not broken in every case, only most of them.
- Extension 4a fails on both wording cases. The filter compares allergen and
  restriction with `===` after lowercasing, so `"peanut"` does not match
  `"peanuts"` and `"tree nuts"` does not match `"nuts"`. In both cases the
  customer is shown a dish they explicitly said they cannot eat.
- Extension 3b fails: the premium tier is capped at $35 rather than being
  unbounded, so the customer on the most permissive tier is the only one who
  cannot see a $40 item.
- Extension 5a fails: `GET /api/foods` returns every food regardless of the
  caller's saved preferences, including a dish the customer is allergic to.
  Filtering is presentation-only in the React client; any other caller of the
  API sees the unfiltered menu.

## Use Case #15: AI Chat Assistant

Test file:
- `proj1/tests/test_chat_assistant_pytest.py`

Runner:
- `proj1/tests/run_chat_assistant_pytest.sh`

Output location:
- `proj1/test-output/`

Setup:
1. Start the backend:
   `cd food-seer-backend`
   `mvn spring-boot:run`
2. From the repository root, run:
   `proj1/tests/run_chat_assistant_pytest.sh`
3. `ChatServiceImpl` posts to a local Ollama at `http://localhost:11434` using
   the `qwen2.5:1.5b` model. Both values are compile-time constants, so the
   feature cannot be pointed anywhere else without rebuilding the backend.

Note on approach:
- Two of these tests are conditional on whether Ollama is running, because the
  interesting behaviour differs. `test_the_assistant_answers_a_greeting` runs
  only when Ollama is reachable; `test_an_unreachable_model_is_reported_as_a_failure`
  runs only when it is not. The file detects which and skips the other.

Test Cases:
- The chat endpoint is called with no credentials.
- Extension 1a: a driver account calls the chat endpoint.
- Main success scenario: a customer sends a greeting and receives a reply
  (requires Ollama running with `qwen2.5:1.5b` pulled).
- Extension 4a: a customer sends a message while Ollama is unreachable.

Known Result:
- Authentication is enforced: an unauthenticated call returns 401.
- Extension 1a passes: a driver receives 403. Note this documents an
  inconsistency rather than endorsing it -- DRIVER is absent from this
  endpoint's role list while present on the order endpoints, which reads as an
  oversight rather than a decision.
- The main success scenario is UNVERIFIED. Ollama was not installed and running
  on the test machine, so `test_the_assistant_answers_a_greeting` skipped. No
  test in this suite demonstrates that the assistant ever produces a real
  answer. This is a genuine gap in our coverage, not a passing result.
- Extension 4a fails, and this is the code-rot finding. With Ollama
  unreachable, the backend returned:

      HTTP 200
      {"message": "Error: I/O error on POST request for
                   \"http://localhost:11434/api/chat\": Connection refused"}

  `ChatServiceImpl` wraps the entire call in `catch (Exception)` and returns
  the exception text in the same `message` field a real answer uses, with a
  200 status. A client cannot distinguish a working assistant from a dead one,
  and the user is shown raw internal exception text -- including the internal
  host and port -- rendered as though the assistant had said it.

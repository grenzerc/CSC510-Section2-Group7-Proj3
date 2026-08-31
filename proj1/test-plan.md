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

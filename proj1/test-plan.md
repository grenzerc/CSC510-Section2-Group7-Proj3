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



## Use Case #2: Update Food Preferences

Test file:
- `proj1/tests/test_customer_preferences_pytest.py`

Output:
- `proj1/test-output/customer-preferences-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. Run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_customer_preferences_pytest.py`

Test Cases:
- Main success scenario: Registers and logs in as a customer, updates the cost preference and dietary restrictions, and verifies the updated values are returned.
- Success postcondition: Updates the customer’s preferences, retrieves the customer profile in a separate request, and verifies the saved values persist.
- Extension 3a: Submits a cost preference not offered by Food Seer and expects the system to reject the unsupported value.
- Extension 3b: Submits a valid cost preference with no dietary restrictions and verifies the system accepts an empty dietary-restriction value.


Known Result:
- The main customer preference update path passes
- The saved preference values persist and can be retrieved from the customer profile
- Extension 3a currently fails because the backend returns HTTP 200 and stores the unsupported value one-million-dollars instead of returning HTTP 400 and rejecting it.
- Extension 3b passes because Food Seer allows customers to save preferences without selecting dietary restrictions.
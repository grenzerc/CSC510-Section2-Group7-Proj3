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



## Use Case #16: Update Food Preferences

Test file:
- `proj1/tests/test_customer_preferences_pytest.py`

Output:
- `proj1/test-output/customer-preferences-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. From the repository root, run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_customer_preferences_pytest.py`

Test Cases:
- Main success scenario: registers and logs in as a customer, updates the cost preference and dietary restrictions, and verifies the updated values are returned.
- Success postcondition: retrieves the customer profile in a separate request and verifies that the saved values persist.
- Extension 3a: submits a cost preference not offered by Food Seer and expects the system to reject it.
- Extension 3b: submits a valid cost preference without dietary restrictions and verifies that an empty dietary-restriction value is accepted.

Known Result:
- The main preference-update scenario passes.
- The updated values persist and can be retrieved.
- Extension 3b passes.
- Extension 3a fails because the backend returns HTTP 200 and stores `one-million-dollars` instead of rejecting it with HTTP 400.




## Use Case #17: Browse Food Inventory

Test file:
- `proj1/tests/test_browse_food_inventory_pytest.py`

Output:
- `proj1/test-output/browse-food-inventory-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. From the repository root, run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_browse_food_inventory_pytest.py`

Test Cases:
- Main success scenario: authenticates a customer, retrieves the food inventory, and verifies that foods are returned.
- Displayed information: verifies that returned foods contain the information needed by the inventory page.
- Extension 1a: requests the inventory without authentication and verifies that access is rejected.
- Success postcondition: retrieves the inventory twice and verifies that browsing does not modify it.

Known Result:
- All four tests pass.
- Authenticated customers can retrieve the inventory.
- Unauthenticated inventory requests are rejected.
- Browsing the inventory does not change stored inventory information.




## Use Case #18: Create a Food Order

Test file:
- `proj1/tests/test_create_food_order_pytest.py`

Output:
- `proj1/test-output/create-food-order-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. From the repository root, run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_create_food_order_pytest.py`

Test Cases:
- Main success scenario: authenticates a customer, selects food, creates an order, and verifies the returned order information.
- Success postcondition: creates an order and verifies that it appears in the customer's personal orders section.
- Extension 7a: bypasses the frontend empty-cart protection and expects the backend to reject an order containing no food.
- Extension 4a: bypasses the frontend stock limit and expects the backend to reject a quantity greater than the available stock.

Known Result:
- The main order-creation scenario passes.
- A successfully created order appears in the customer's personal orders.
- Extension 7a fails because the backend returns HTTP 200 and creates an empty order instead of rejecting it.
- Extension 4a fails because the backend returns HTTP 200 and creates an order exceeding available stock instead of rejecting it.




## Use Case #19: View Personal Orders

Test file:
- `proj1/tests/test_view_personal_orders_pytest.py`

Output:
- `proj1/test-output/view-personal-orders-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. From the repository root, run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_view_personal_orders_pytest.py`

Test Cases:
- Main success scenario: creates an order and verifies that the authenticated customer can retrieve it from their personal orders.
- Extension 2b: verifies that one customer does not receive another customer's order.
- Extension 2a: verifies that a newly registered customer receives an empty personal-order list.
- Extension 3a: verifies that repeated food entries representing multiple units are preserved in the order details.

Known Result:
- All four tests pass.
- Customers can retrieve their own orders.
- Personal-order results do not include another customer's order.
- New customers receive an empty order list.
- Repeated food entries are preserved.




## Use Case #20: Rate Food from a Fulfilled Order

Test file:
- `proj1/tests/test_rate_fulfilled_order_pytest.py`

Output:
- `proj1/test-output/rate-fulfilled-order-pytest.txt`

Setup:
1. Start MySQL.
2. Start the Food Seer backend on port 8080.
3. From the repository root, run:
   `python -m pytest -p no:cacheprovider -vv proj1/tests/test_rate_fulfilled_order_pytest.py`

Test Cases:
- Main success scenario: creates and fulfills an order, rates its food, rating count and rated-food record are updated.
- Extension 6a: submits a second rating for the same food and order and verifies that the duplicate rating is rejected.
- Extension 2a: bypasses the frontend "Wait for delivery" restriction and verifies that food from an unfulfilled order cannot be rated.
- Extension 6b: uses a different authenticated customer to rate another customer's fulfilled order and expects the request to be rejected.

Known Result:
- The main fulfilled-order rating scenario passes.
- Duplicate ratings are rejected.
- Ratings for unfulfilled orders are rejected.
- Extension 6b fails because the backend returns HTTP 200 and accepts a rating from a customer who does not own the order.
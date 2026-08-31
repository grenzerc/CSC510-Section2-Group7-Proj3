# Project 1 Use Cases

## Use Case #1

Part: Driver Registration and Dashboard Access

Name: Register and login as driver

Primary Actor: Driver

Stakeholders and Interests:
- Drivers: want to create an account and access their driver dashboard.
- Company and admin: want drivers to be registered with the correct role.
- Customers: benefit from available registered drivers for order delivery.

Preconditions:
- Frontend and backend are running correctly.
- The driver does not already have an account with the chosen username or email.

Trigger:
- A potential driver chooses to make an account.

Main Success Scenario:
1. Driver accesses the recommendation web page.
2. Driver clicks the register button.
3. Driver enters username, email, password, and password confirmation.
4. Driver selects Driver as the role.
5. Driver submits registration.
6. System creates the driver account and associated driver statistics record.
7. Driver logs in with the just-created account.
8. System redirects the driver to the driver dashboard.
9. Driver checks that the dashboard content and statistics load.

Extensions:
- 3a. User enters incomplete or invalid information.
  Error message prompts user to enter the information correctly.
- 3b. Password and password confirmation do not match.
  Error message prompts user to have passwords match.
- 4a. User does not select a role.
  Error message prompts user to select a role.
- 5a. Email account is already being used.
  Error message prompts user to select a different email address.
- 7a. Login fails due to invalid credentials.
  Error message prompts user to enter valid credentials.
- 9a. Account exists but dashboard content does not load.
  Error message says content does not exist or cannot be loaded.

Postconditions:
- New driver's account exists with the proper role.
- The account can be logged into and accessed.
- Relevant statistics and dashboard information can be accessed.




## Use Case #16

Part: Customer Preferences

Name: Update Food Preferences

Primary Actor: Customer

Stakeholders and Interests:
- Customer: Wants current cost and dietary preferences saved to their account.
- Company: Needs to associate preferences with the correct authenticated account.

Preconditions:
- The customer has an existing Food Seer account.
- The customer is authenticated.

Trigger:
- The customer chooses to view or modify their food preferences.

Main Success Scenario:
1. The system retrieves the customer's existing food preferences.
2. The system displays the existing cost preference and dietary restrictions.
3. The customer changes the cost preference and/or dietary restrictions.
4. The customer submits the changes.
5. The system identifies the customer using the authenticated account.
6. The system saves the submitted preferences to the customer's account.
7. The system redirects the customer to the recommendations page.

Extensions:
- 1a. Existing preferences cannot be retrieved.
  The system displays an empty preference form and allows the customer to continue.
- 3a. The customer submits an unsupported cost preference.
  The system should reject the unsupported value.
- 3b. The customer selects no dietary restrictions.
  The system stores the dietary-restriction value as an empty string.
- 4a. The save request fails.
  The system informs the customer that the preferences could not be saved.
- 5a. The customer is not authenticated.
  The system rejects the update.
- 5b. No account matches the authenticated username.
  The system returns a not-found response.

Postconditions:
- Success: The submitted cost preference and dietary restrictions are stored in the customer's account, and the customer is redirected to the recommendations page.
- Failure: The customer is not redirected to the recommendations page.

## Use Case #17

Part: Food Inventory

Name: Browse Food Inventory

Primary Actor: Customer

Stakeholders and Interests:
- Customer: Wants to browse food items and see their prices, quantities, ratings, and allergy information.
- Company: Wants authenticated customers to receive current food inventory information.

Preconditions:
- The customer has an existing Food Seer account.
- The customer is authenticated.
- The food inventory can be retrieved.

Trigger:
- The customer navigates to the food inventory page.

Main Success Scenario:
1. The system verifies the customer's authentication.
2. The system retrieves the food inventory.
3. The system displays the food items and their available information.
4. The customer may search for food by name.
5. The customer may limit the displayed results to foods currently in stock.
6. The customer may sort the displayed foods by name, price, quantity, or rating.
7. The system displays the number of matching foods.
8. The customer may choose to continue to order creation.

Extensions:
- 1a. The customer is not authenticated.
  The system rejects the inventory request.
- 2a. The inventory cannot be retrieved.
  The system redirects the customer away from the inventory page.
- 4a. No foods match the customer's search or filter criteria.
  The system displays "No foods found matching your criteria."
- 8a. The customer returns to recommendations instead of creating an order.
  The system navigates to the recommendations page.

Postconditions:
- Success: The customer can view the inventory without changing stored food or order data.
- Failure: No inventory data is displayed.

## Use Case #18

Part: Customer Ordering

Name: Create a Food Order

Primary Actor: Customer

Stakeholders and Interests:
- Customer: Wants to select food, review the cost, and place an order.
- Company: Wants orders stored and associated with the correct customer.
- Driver: Needs valid customer orders to become available for delivery.

Preconditions:
- The customer has an existing Food Seer account.
- The customer is authenticated.
- At least one food item is available in the inventory.

Trigger:
- The customer navigates to the order-creation page.

Main Success Scenario:
1. The system retrieves the available food items.
2. The system displays food items with positive stock quantities.
3. The customer adds one or more food items to the cart.
4. The customer selects quantities that don't exceed the displayed stock.
5. The system calculates the item subtotal, delivery cost, and total cost.
6. The customer enters a name for the order.
7. The customer submits the order.
8. The system associates the order with the authenticated customer.
9. The system saves the order with a placed and unfulfilled status.
10. The system informs the customer that the order was placed successfully.
11. The system redirects the customer to the orders page.

Extensions:
- 1a. The customer cannot be authenticated or food retrieval fails.
  The system redirects the customer away from the order-creation page.
- 3a. A recommended food item is out of stock.
  The system warns the customer that the item is unavailable.
- 4a. The customer requests more units than are available.
  The system should reject the order.
- 6a. The customer does not provide an order name.
  The system asks the customer to enter a name.
- 7a. The customer attempts to place an order with an empty cart.
  The system prevents submission and asks the customer to add food to the cart.
- 8a. A requested food item does not exist.
  The system rejects the order and informs the customer that order creation failed.

Postconditions:
- Success: A new unfulfilled order is stored and associated with the authenticated customer.
- Failure: A valid order is not created, and the customer remains on the order-creation page.

## Use Case #19

Part: Customer Orders

Name: View Personal Orders

Primary Actor: Customer

Stakeholders and Interests:
- Customer: Wants to view their own orders and current order information.
- Company: Needs to prevent customers from viewing another customer's personal order list.

Preconditions:
- The customer has an existing Food Seer account.
- The customer is authenticated.

Trigger:
- The customer navigates to the orders page.

Main Success Scenario:
1. The system identifies the authenticated customer.
2. The system retrieves the orders associated with that customer.
3. The system displays each order's name, identifier, item count, total cost, food items, and status.
4. The customer may filter the displayed orders by all, pending, or fulfilled.

Extensions:
- 1a. The customer is not authenticated.
  The system rejects the request or redirects the customer away from the orders page.
- 2a. The customer has no orders.
  The system displays "No orders found" and provides a button to create an order.
- 2b. Orders belonging to another customer exist.
  The system excludes those orders from the authenticated customer's results.
- 3a. An order contains multiple units of the same food.
  The system preserves the repeated food entries when returning the order.

Postconditions:
- Success: The customer can view and filter their own stored orders without changing them.
- Failure: The customer's personal orders are not displayed.

## Use Case #20

Part: Customer Feedback

Name: Rate Food from a Fulfilled Order

Primary Actor: Customer

Stakeholders and Interests:
- Customer: Wants to rate food received through a fulfilled order.
- Company: Wants food ratings based on completed orders and wants to prevent duplicate ratings.

Preconditions:
- The customer has an existing Food Seer account and is authenticated.
- The order exists and contains the food being rated.
- The order has been fulfilled.
- The food has not already been rated for that order.

Trigger:
- The customer selects a rating for a food item in a fulfilled order.

Main Success Scenario:
1. The customer views a fulfilled personal order.
2. The system displays rating controls for an unrated food item.
3. The customer selects a rating from the available values.
4. The customer submits the rating.
5. The system verifies that the order is fulfilled and contains the food.
6. The system verifies that the food has not already been rated for that order.
7. The system updates the food's average rating and number of ratings.
8. The system records that the food was rated for the order.
9. The system informs the customer that the rating was submitted successfully.
10. The system displays the food as rated after the page is refreshed.

Extensions:
- 2a. The order has not been fulfilled.
  The system displays "Wait for delivery" instead of displaying rating controls.
- 5a. The order or food cannot be found.
  The system returns a not-found response.
- 6a. The food has already been rated for that order.
  The system doesn't allow for duplicate rating.
- 6b. A different authenticated customer attempts to rate the order.
  The system should reject the rating because the customer does not own the order.

Postconditions:
- Success: The food's rating information is updated, and the order records that the food has been rated.
- Failure: The rating information should remain unchanged.
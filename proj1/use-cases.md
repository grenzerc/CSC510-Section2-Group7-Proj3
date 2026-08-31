# Project 1 Use Cases

This document will be used to write our use cases. Recall the format, per project 1a specs:

Part:	What it says
Name:	Verb + noun, actor's goal ("Place order")
Primary actor:	Who wants the goal
Stakeholders & interests:	Who else cares, what they want
Preconditions:	Must be true before start
Trigger:	Event that kicks it off
Main success scenario:	Numbered steps, actor ↔ system, happy path only
Extensions:	Numbered variations/failures, keyed to steps ("3a: card declined → ...")
Postconditions:	Guaranteed true on success



NOTE: the order of cases don't matter, as far as I'm aware. We can change these later.

## Use Case #1

### Part
Driver Registration and Dashboard Access

### Name
Register and login as driver

### Primary Actor
Driver

### Stakeholders and interests
Drivers, company & admin, customers

### Preconditions
Frontend and Backend are running correctly

### Trigger
Potential drivers chooses to make an account

### Main success scenario
1. Driver access main web page
2. Clicks register button
3. Enters username, password, and password confirmation
4. Selects Role as driver
5. Submit registration
6. Logs in with the just-created account
7. Checks that application redirects to the driver dashboard
8. Check that the driver dashboard content and statistics loads

### Extensions
3a. User enters incomplete or invalid information.

Error message prompts user to enter correctly

3b. Password and password confirmation do not match

Error message prompts user to have passwords match

4a. User does not select a role

Error message prompts user to select a role

5a. Email account already being used

Error message prompts user to select a different email address

6a. Login fails due to invalid credentials

Error message prompts user to enter valid credentials

8a. Account exists but nothing loads

Error message says content does not exist or cannot be loaded

### Postconditions
New Driver's account exists with proper role

The account can be logged into and access

Relevant statistics/dashboard information can be accessed

## Use Case #2

### Part
Duplicate account prevention

### Name
User is prevented from making a new account with the same email as existing account

### Primary actor
User

### Stakeholders & interests
new users: need appropriate feedback when registration fails

Existing users: need protection from others using their email for another account

Admin: needs errors to be handled appropriate instead of causing crashes

Business: needs user accounts to be unique

### Preconditions
1. Frontend and Backend are running correctly
2. An account already exists with the email the user is trying to register a new account with
3. The user trying to register isn't already logged in

### Trigger
User attempts to register a new account with an email that is already being used on another account.

### Main success scenario
1. User accesses the user registration page
2. User enters a new username for their desired account
3. User enters an email that is already tied to an existing, registered account
4. User enters password and password confirmation
5. User selects role(driver, staff, customer)
6. User submits registration form
7. System detects that the email is already being used and rejects the registration attempt
8. Frontend displays error message that the email is already being used, and that a different address must be used

### Extensions
2a. User enters a username that is already being used with a different account

Error message telling user that the name is being used already

4a. Password and password confirmation do not match

Error message telling user that their passwords do not match

5a. User does not select a role

Error message telling user that a role must be selected

7a. System fails to detect duplicate email before saving

System rejects registration on database side, and the front end should produce a specific error for this instead of a generic internal error

8a. Frontend displays only a generic registration error

Error informs user only that registration failed without specifying that it was due to duplicate email

### Postconditions
1. The new account with the duplicate email is not created
2. The old account that already used that email is unchanged
3. Frontend provides error message informing user that registration failed due to duplicate email

## Use Case #3

### Part
Registration Error Handling

### Name
User receives a specific error message based on how account registration fails

### Primary actor
User

### Stakeholders & interests
New users: Need information on why their registration attempt failed

Existing users: need to be protected from duplicate accounts using their identity

Business: Wants new users to be able to complete registration by knowing why attempts failed.

Admin: Needs registration problems to be handled appropriately and in an informative way for users

### Preconditions
1. Frontend and backend are working correctly
2. User is on the registration page
3. User not logged in
4. Validation rules exist on backend for username, password, password confirmation, email, and role

### Trigger
User submits registration form with data field entries that are incorrect, causing registration to fail

### Main success scenario
1. User accesses the user registration page
2. User enters registration information
3. User submits registration form
4. Backend rejects registration for a specific reason
5. Backend sends error response to frontend
6. Frontend displays a specific, clear error message explaining why specifically registration failed
7. User remains on registration form and can correct the form and submit again

### Extensions
2a. User enters a username that is already taken

Frontend displays an error message telling the user that the username is already taken

2b. User enters an email that is already being used by another account

Frontend displays an error message telling the user that the email is already tied to another account

2c. User enters email in an invalid format

Frontend displays an error message telling the user that the email must be formatted in a certain way

2d. User enters password in an invalid format

Frontend displays an error message telling user that passwords must be formatted in a certain way

2e. User enters a password and password confirmation that do not match

Frontend displays an error message telling user that password and password confirmation must be the same

2f. User does not enter a role

Frontend displays an error message telling user that a role must be selected

4a. Backend returns an unexpected server error

Frontend displays a registration error message

5a. Backend returns generic error message

Frontend displays a generic error message

### Postconditions
1. Invalid registration is not completed
2. No invalid user account is created
3. User sees error message specific to the cause of failure
4. User remains on the registration form and is able to edit it and submit again

## Use Case #4

### Part
Login Redirection

### Name
Login redirects user successfully based on user's role

### Primary actor
User

### Stakeholders & interests
User: wants to reach the correct page for their role after logging in

Admin: wants users to access only content appropriate for their role

Business: want users to have the correct workflow in a secure way

### Preconditions
1. Frontend and backend are working correctly
2. User already has a registered account
3. User not logged in
4. User associated with a valid role(staff, admin, customer, driver)

### Trigger
User submits valid login

### Main success scenario
1. User acceses the login page
2. User enters valid username and password
3. User submits login form
4. User's form is authenticated
5. System identifies user's role
6. Frontend redirects user to the correct page for their role
7. User sees the dashboard appropriate to their role

### Extensions
2a. User enters invalid username or password

Login is rejected and an error message stating an incorrect username or password was entered is displayed

4a. Backend authentication is unavailable

Error message is displayed and user is not redirected

5a. User account not associated with a role

Error message displayed, user is not redirected to a dashboard

6a. User is assigned to admin role

User is redirected to admin dashboard

6b. User is assigned to staff role

User is redirected to staff dashboard

6c. User is assigned to driver role

User is redirected to driver dashboard

6d. User is assigned to customer role

User is redirected to customer dashboard

6e. User is redirected to the wrong page for their role

User loses access to desired features, system should redirect them correctly or deny access

### Postconditions
1. User is authenticated
2. User session is stored by the frontend
3. User is redirected to page appropriate to their role
4. User can access features for their role
5. User is prevented from accessing pages outside their role permissions

## Use Case #5

### Part
Unauthorized User Is Blocked From Restricted Dashboard

### Name
User restricted access features they aren't allowed to see

### Primary actor
User

### Stakeholders & interests
1. User: Wants to know why they can or can't access certain features/information
2. Admin: wants role based permissions enforced properly
3. Business: Wants data protected from unauthorized access

### Preconditions
1. Frontend and backend are running correctly
2. Restricted pages actually exist, as per staff, admin, and driver pages
3. User either not logged in, or logged into a role that does not have permission to access restricted content

### Trigger
User attempts to open a page they are not authorized to access

### Main success scenario
1. User attempts to access restricted page/feature
2. System checks to see whether user is authenticated
3. System checks to see whether user's role is authorized for that page
4. System blocks access because user is not authorized for that content
5. Frontend redirects user to a page appropriate for their permissions
6. Frontend displays an error message explaining why user can't access the desired page

### Extensions
2a. User is not logged in

User is redirected to login page

3a. User with customer role attempts to access driver dashboard

Access is blocked and user is redirected to customer-appropriate page

3b. User with customer role attempts to access admin dashboard

Access is blocked and user is redirected to customer-appropriate page

3c. User with customer role attempts to access staff dashboard

Access is blocked and user is redirected to customer-appropriate page

4a. API request is made without valid token

Backend rejects request with an unauthorized response

5a. Frontend fails to prevent access to restricted page

Backend authorization prevents restricted content from loading

6a. System does not display a clear, specific error message

User redirected to appropriate page

### Postconditions
1. Unauthorized user cannot view restricted content
2. Unauthorized user cannot perform restricted actions
3. Backend and frontend do not expose restricted data
4. User redirected to appropriate page


## Use Case #11

### Part
Administrative Role Management

### Name
Change a user's role

### Primary Actor
Admin

### Stakeholders and interests
- Admin: wants to grant and revoke authority accurately and keep the system administrable.
- Affected user: wants the access their job requires, and no more.
- Company: wants least privilege enforced and an admin account always available.

### Preconditions
- Frontend and backend are running.
- An admin is logged in.
- At least one other user account exists.

### Trigger
- An admin needs to promote or demote a user, for example making a new hire staff.

### Main success scenario
1. Admin opens the User Management page.
2. System returns every user account with its current role.
3. Admin selects the user to change.
4. Admin chooses the new role.
5. Admin submits the change.
6. System stores the new role and returns the updated user record.
7. The affected user holds the new role's authority on their next login.

### Extensions
- 2a. A non-admin requests the user list.
  System returns 403; the endpoint is guarded by hasRole('ADMIN'). Handled.
- 5a. The user id does not exist.
  Service returns null and the controller returns 404. Handled.
- 5b. The submitted role is not a real role, for example "ROLE_WIZARD" or an empty string.
  NOT handled. UserServiceImpl.updateUserRole calls user.setRole(role) with no validation
  against any role registry, so the system returns 200 and stores the value. The account can
  still log in but is authorized for nothing, and no screen shows the role is invalid.
- 5c. The admin demotes the last remaining admin, including themselves.
  NOT handled. There is no last-admin guard. Because only an admin may change roles, the
  deployment permanently loses all administrative access.
- 5d. The role is changed while the affected user holds a valid JWT.
  NOT handled. The token keeps the old role until it expires; there is no revocation, so a
  demoted user retains their old authority for the life of the token.
- 4a. The set of legal roles is undefined in the backend.
  Two divergent registries exist: FoodSeer.config.Roles lists CUSTOMER and STAFF, and
  FoodSeer.constant.Roles lists CUSTOMER, STAFF and DRIVER. Neither is consulted here.

### Postconditions
- The target user's stored role equals the submitted value.
- The admin sees the updated role in the user list.

## Use Case #12

### Part
Inventory and Menu Management

### Name
Manage the food inventory

### Primary Actor
Staff

### Stakeholders and interests
- Staff: want stock levels to match what the kitchen actually has.
- Customers: want to order only food that exists.
- Company: wants menu and stock changes restricted to people who run the store.

### Preconditions
- Frontend and backend are running.
- A staff account is logged in.
- The inventory record exists.

### Trigger
- Stock levels change, or a menu item must be added, corrected or removed.

### Main success scenario
1. Staff opens the Inventory Management page.
2. System returns the current inventory.
3. Staff edits the amount held for one or more foods.
4. Staff submits the updated inventory.
5. System saves the inventory and returns the stored result.
6. The new amounts appear to customers browsing available food.

### Extensions
- 2a. The request carries no credentials.
  System returns 401; all non-auth endpoints require authentication by default. Handled.
- 4a. A customer submits an inventory update.
  NOT handled. InventoryController guards both endpoints with
  hasAnyRole('ADMIN', 'STAFF', 'CUSTOMER'), so a customer account can rewrite the stock level
  of every item in the store.
- 4b. A customer or driver creates, edits or deletes a menu item.
  NOT handled. FoodController declares no authorization at all on POST /api/foods,
  POST /api/foods/updateFood or DELETE /api/foods/{id}. Any authenticated account can add or
  remove menu items.
- 4c. Staff submits a negative amount or price on a food update.
  System returns 400. Handled.
- 4d. Staff deletes a food that appears in an unfulfilled order.
  Service raises IllegalStateException and the controller returns 409 with an explanation.
  Handled.
- 4e. Staff creates a food whose name already exists.
  System returns 409. Handled.

### Postconditions
- The stored inventory reflects the submitted amounts.
- Customers browsing food see the updated availability.

## Use Case #13

### Part
Driver Statistics

### Name
View driver delivery statistics

### Primary Actor
Driver

### Stakeholders and interests
- Driver: wants an accurate record of deliveries completed and earnings.
- Company: wants driver performance data available to the driver and to management.
- Every driver: wants their own earnings kept private from other users.

### Preconditions
- Frontend and backend are running.
- A driver account exists with an associated statistics record, created at registration.

### Trigger
- The driver opens their dashboard.

### Main success scenario
1. Driver logs in and the system routes them to the driver dashboard.
2. Dashboard requests the statistics belonging to the logged-in driver.
3. System returns that driver's delivery counts and earnings.
4. Driver reviews their statistics.

### Extensions
- 2a. The request carries no credentials at all.
  NOT handled. SpringSecurityConfig permits every GET under /api/driverStats without
  authentication, and DriverStatsController declares no authorization. The @PreAuthorize
  annotation is imported in that file but never applied, so the guard appears to have been
  intended and forgotten. Anyone who can reach the server reads driver statistics.
- 2b. A user requests another driver's statistics.
  NOT handled. The endpoint selects the record from a username query parameter and never
  compares it to the authenticated principal, so any username can be substituted.
- 2c. The requested username does not exist, or belongs to a customer rather than a driver.
  NOT handled cleanly. The controller returns 200 with whatever the service produced instead
  of 404, so a caller cannot distinguish "no such driver" from "a driver with no deliveries".
- 1a. The dashboard fails to render even when the data is available.
  The project's own DriverDashboardTest#testDriverDashboardLoads does not pass, so the render
  path above this use case is unverified by the existing suite.

### Postconditions
- The driver has seen their current delivery statistics.

## Use Case #14

### Part
Food Recommendation

### Name
Get a food recommendation

### Primary Actor
Customer

### Stakeholders and interests
- Customer: wants to be shown food they can afford and are able to eat safely.
- Company: wants recommendations to drive orders without recommending unsafe food.
- Staff: want recommendations limited to food actually on the menu.

### Preconditions
- Frontend and backend are running.
- A customer is logged in and has saved a cost preference and dietary restrictions.
- At least one food exists.

### Trigger
- The customer opens the Recommendations page.

### Main success scenario
1. Customer opens Recommendations.
2. System loads the customer's profile and the full food list.
3. System removes foods priced above the customer's budget tier.
4. System removes foods whose allergen list matches one of the customer's dietary restrictions.
5. System displays the remaining foods with prices and average ratings.

### Extensions
- 3a. Cost preference is "no-limit" or an unrecognized value.
  No price filter is applied and all foods are shown. Handled.
- 3b. Cost preference is "premium".
  NOT handled. The premium tier filters to foods priced at $35 or less rather than being
  unbounded, so the customer who chose the most permissive real tier is the only one who
  cannot see the most expensive items on the menu.
- 4a. A dietary restriction is worded differently from the food's allergen.
  NOT handled, and safety-critical. Matching is exact string equality after lowercasing, so a
  restriction of "peanuts" does not match an allergen recorded as "peanut", and "nuts" does not
  match "tree nuts". The food is presented as safe to a customer who declared they cannot eat it.
- 4b. A food has an empty allergen list.
  It is treated as safe for every restriction. Handled by design, but the design assumes the
  allergen data is complete.
- 2a. The profile or food request fails.
  Handled poorly. The page logs to the browser console and navigates back to the login route
  with no message explaining why.
- 5a. Filtering is presentation only.
  NOT handled. The API returns every food regardless of the customer's preferences and all
  filtering happens in the browser, so any direct API call or alternate client sees the
  unfiltered menu.

### Postconditions
- The customer has seen a list of foods they believe respects their budget and restrictions.

## Use Case #15

### Part
AI Assistant

### Name
Chat with the food assistant

### Primary Actor
Customer

### Stakeholders and interests
- Customer: wants a usable answer, and to be told plainly when the assistant is unavailable.
- Company: wants the assistant to talk about food that is actually on the menu.
- Staff: want the assistant not to contradict the real inventory.

### Preconditions
- Frontend and backend are running.
- The user is logged in as an admin, staff or customer.
- An Ollama server is reachable at localhost:11434 with the qwen2.5:1.5b model pulled.

### Trigger
- The customer opens the chatbot and sends a message.

### Main success scenario
1. Customer types a message and sends it.
2. System builds a request containing a fixed system prompt and the customer's message.
3. If the message asks for a recommendation, system appends the current menu with prices and
   allergens.
4. System posts the request to the local Ollama chat API.
5. System returns the assistant's reply.
6. Customer reads the reply.

### Extensions
- 4a. Ollama is not running, or the model has not been pulled.
  NOT handled. ChatServiceImpl catches every exception and returns HTTP 200 with the body
  "Error: " followed by the exception text, placed in the same field as a real answer. The
  client cannot distinguish failure from success, and internal exception text is shown to the
  user as though the assistant had said it.
- 3a. The customer asks for a recommendation in words the code does not anticipate.
  NOT handled. Intent is detected by three hardcoded substrings: "what should i eat",
  "recommend food" and "suggest food". "What do you recommend?" or "I'm hungry, any ideas?"
  never attach the menu, so the model answers about food it cannot see and may invent items
  that are not for sale.
- 3b. The customer has saved dietary restrictions.
  NOT handled. Only the menu is sent. The customer's stored restrictions are never included in
  the prompt, so the assistant can recommend a dish the customer already declared they cannot eat.
- 4b. The assistant must be pointed at a different host or model.
  NOT handled. The Ollama URL and model name are compile-time constants, so any change
  requires editing and rebuilding the backend.
- 1a. A driver opens the chatbot.
  System returns 403. DRIVER is absent from this endpoint's role list while it is present on
  the order endpoints, which reads as an oversight rather than a decision.

### Postconditions
- The customer has received a reply, or an error message rendered as though it were a reply.


## Use Case #16

### Part
Customer Preferences

### Name
Update Food Preferences

### Primary Actor
Customer

### Stakeholders and interests
- Customer: Wants current cost and dietary preferences saved to their account.
- Company: Needs to associate preferences with the correct authenticated account.

### Preconditions
- The customer has an existing Food Seer account.
- The customer is authenticated.

### Trigger
- The customer chooses to view or modify their food preferences.

### Main success scenario
1. The system retrieves the customer's existing food preferences.
2. The system displays the existing cost preference and dietary restrictions.
3. The customer changes the cost preference and/or dietary restrictions.
4. The customer submits the changes.
5. The system identifies the customer using the authenticated account.
6. The system saves the submitted preferences to the customer's account.
7. The system redirects the customer to the recommendations page.

### Extensions
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

### Postconditions
- Success: The submitted cost preference and dietary restrictions are stored in the customer's account, and the customer is redirected to the recommendations page.
- Failure: The customer is not redirected to the recommendations page.

## Use Case #17

### Part
Food Inventory

### Name
Browse Food Inventory

### Primary Actor
Customer

### Stakeholders and interests
- Customer: Wants to browse food items and see their prices, quantities, ratings, and allergy information.
- Company: Wants authenticated customers to receive current food inventory information.

### Preconditions
- The customer has an existing Food Seer account.
- The customer is authenticated.
- The food inventory can be retrieved.

### Trigger
- The customer navigates to the food inventory page.

### Main success scenario
1. The system verifies the customer's authentication.
2. The system retrieves the food inventory.
3. The system displays the food items and their available information.
4. The customer may search for food by name.
5. The customer may limit the displayed results to foods currently in stock.
6. The customer may sort the displayed foods by name, price, quantity, or rating.
7. The system displays the number of matching foods.
8. The customer may choose to continue to order creation.

### Extensions
- 1a. The customer is not authenticated.
  The system rejects the inventory request.
- 2a. The inventory cannot be retrieved.
  The system redirects the customer away from the inventory page.
- 4a. No foods match the customer's search or filter criteria.
  The system displays "No foods found matching your criteria."
- 8a. The customer returns to recommendations instead of creating an order.
  The system navigates to the recommendations page.

### Postconditions
- Success: The customer can view the inventory without changing stored food or order data.
- Failure: No inventory data is displayed.

## Use Case #18

### Part
Customer Ordering

### Name
Create a Food Order

### Primary Actor
Customer

### Stakeholders and interests
- Customer: Wants to select food, review the cost, and place an order.
- Company: Wants orders stored and associated with the correct customer.
- Driver: Needs valid customer orders to become available for delivery.

### Preconditions
- The customer has an existing Food Seer account.
- The customer is authenticated.
- At least one food item is available in the inventory.

### Trigger
- The customer navigates to the order-creation page.

### Main success scenario
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

### Extensions
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

### Postconditions
- Success: A new unfulfilled order is stored and associated with the authenticated customer.
- Failure: A valid order is not created, and the customer remains on the order-creation page.

## Use Case #19

### Part
Customer Orders

### Name
View Personal Orders

### Primary Actor
Customer

### Stakeholders and interests
- Customer: Wants to view their own orders and current order information.
- Company: Needs to prevent customers from viewing another customer's personal order list.

### Preconditions
- The customer has an existing Food Seer account.
- The customer is authenticated.

### Trigger
- The customer navigates to the orders page.

### Main success scenario
1. The system identifies the authenticated customer.
2. The system retrieves the orders associated with that customer.
3. The system displays each order's name, identifier, item count, total cost, food items, and status.
4. The customer may filter the displayed orders by all, pending, or fulfilled.

### Extensions
- 1a. The customer is not authenticated.
  The system rejects the request or redirects the customer away from the orders page.
- 2a. The customer has no orders.
  The system displays "No orders found" and provides a button to create an order.
- 2b. Orders belonging to another customer exist.
  The system excludes those orders from the authenticated customer's results.
- 3a. An order contains multiple units of the same food.
  The system preserves the repeated food entries when returning the order.

### Postconditions
- Success: The customer can view and filter their own stored orders without changing them.
- Failure: The customer's personal orders are not displayed.

## Use Case #20

### Part
Customer Feedback

### Name
Rate Food from a Fulfilled Order

### Primary Actor
Customer

### Stakeholders and interests
- Customer: Wants to rate food received through a fulfilled order.
- Company: Wants food ratings based on completed orders and wants to prevent duplicate ratings.

### Preconditions
- The customer has an existing Food Seer account and is authenticated.
- The order exists and contains the food being rated.
- The order has been fulfilled.
- The food has not already been rated for that order.

### Trigger
- The customer selects a rating for a food item in a fulfilled order.

### Main success scenario
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

### Extensions
- 2a. The order has not been fulfilled.
  The system displays "Wait for delivery" instead of displaying rating controls.
- 5a. The order or food cannot be found.
  The system returns a not-found response.
- 6a. The food has already been rated for that order.
  The system doesn't allow for duplicate rating.
- 6b. A different authenticated customer attempts to rate the order.
  The system should reject the rating because the customer does not own the order.

### Postconditions
- Success: The food's rating information is updated, and the order records that the food has been rated.
- Failure: The rating information should remain unchanged.

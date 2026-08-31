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
1. Driver accesses the main web page.
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

## Use Case #11

Part: Administrative Role Management

Name: Change a user's role

Primary Actor: Admin

Stakeholders and Interests:
- Admin: wants to grant and revoke authority accurately and keep the system administrable.
- Affected user: wants the access their job requires, and no more.
- Company: wants least privilege enforced and an admin account always available.

Preconditions:
- Frontend and backend are running.
- An admin is logged in.
- At least one other user account exists.

Trigger:
- An admin needs to promote or demote a user, for example making a new hire staff.

Main Success Scenario:
1. Admin opens the User Management page.
2. System returns every user account with its current role.
3. Admin selects the user to change.
4. Admin chooses the new role.
5. Admin submits the change.
6. System stores the new role and returns the updated user record.
7. The affected user holds the new role's authority on their next login.

Extensions:
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

Postconditions:
- The target user's stored role equals the submitted value.
- The admin sees the updated role in the user list.


## Use Case #12

Part: Inventory and Menu Management

Name: Manage the food inventory

Primary Actor: Staff

Stakeholders and Interests:
- Staff: want stock levels to match what the kitchen actually has.
- Customers: want to order only food that exists.
- Company: wants menu and stock changes restricted to people who run the store.

Preconditions:
- Frontend and backend are running.
- A staff account is logged in.
- The inventory record exists.

Trigger:
- Stock levels change, or a menu item must be added, corrected or removed.

Main Success Scenario:
1. Staff opens the Inventory Management page.
2. System returns the current inventory.
3. Staff edits the amount held for one or more foods.
4. Staff submits the updated inventory.
5. System saves the inventory and returns the stored result.
6. The new amounts appear to customers browsing available food.

Extensions:
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

Postconditions:
- The stored inventory reflects the submitted amounts.
- Customers browsing food see the updated availability.


## Use Case #13

Part: Driver Statistics

Name: View driver delivery statistics

Primary Actor: Driver

Stakeholders and Interests:
- Driver: wants an accurate record of deliveries completed and earnings.
- Company: wants driver performance data available to the driver and to management.
- Every driver: wants their own earnings kept private from other users.

Preconditions:
- Frontend and backend are running.
- A driver account exists with an associated statistics record, created at registration.

Trigger:
- The driver opens their dashboard.

Main Success Scenario:
1. Driver logs in and the system routes them to the driver dashboard.
2. Dashboard requests the statistics belonging to the logged-in driver.
3. System returns that driver's delivery counts and earnings.
4. Driver reviews their statistics.

Extensions:
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

Postconditions:
- The driver has seen their current delivery statistics.


## Use Case #14

Part: Food Recommendation

Name: Get a food recommendation

Primary Actor: Customer

Stakeholders and Interests:
- Customer: wants to be shown food they can afford and are able to eat safely.
- Company: wants recommendations to drive orders without recommending unsafe food.
- Staff: want recommendations limited to food actually on the menu.

Preconditions:
- Frontend and backend are running.
- A customer is logged in and has saved a cost preference and dietary restrictions.
- At least one food exists.

Trigger:
- The customer opens the Recommendations page.

Main Success Scenario:
1. Customer opens Recommendations.
2. System loads the customer's profile and the full food list.
3. System removes foods priced above the customer's budget tier.
4. System removes foods whose allergen list matches one of the customer's dietary restrictions.
5. System displays the remaining foods with prices and average ratings.

Extensions:
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

Postconditions:
- The customer has seen a list of foods they believe respects their budget and restrictions.


## Use Case #15

Part: AI Assistant

Name: Chat with the food assistant

Primary Actor: Customer

Stakeholders and Interests:
- Customer: wants a usable answer, and to be told plainly when the assistant is unavailable.
- Company: wants the assistant to talk about food that is actually on the menu.
- Staff: want the assistant not to contradict the real inventory.

Preconditions:
- Frontend and backend are running.
- The user is logged in as an admin, staff or customer.
- An Ollama server is reachable at localhost:11434 with the qwen2.5:1.5b model pulled.

Trigger:
- The customer opens the chatbot and sends a message.

Main Success Scenario:
1. Customer types a message and sends it.
2. System builds a request containing a fixed system prompt and the customer's message.
3. If the message asks for a recommendation, system appends the current menu with prices and
   allergens.
4. System posts the request to the local Ollama chat API.
5. System returns the assistant's reply.
6. Customer reads the reply.

Extensions:
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

Postconditions:
- The customer has received a reply, or an error message rendered as though it were a reply.

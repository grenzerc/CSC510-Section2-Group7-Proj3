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

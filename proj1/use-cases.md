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

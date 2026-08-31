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
Part: Driver Registration and Dashboard Access
Name: Register and login as driver
Primary Actor: Driver
Stakeholders and interests: Drivers, company & admin, customers
Preconditions: Frontend and Backend are running correctly
Trigger: Potential drivers chooses to make an account
Main success scenario:
    1. Driver access main web page
    2. Clicks register button
    3. Enters username, password, and password confirmation
    4. Selects Role as driver
    5. Submit registration
    6. Logs in with the just-created account
    7. Checks that application redirects to the driver dashboard
    8. Check that the driver dashboard content and statistics loads
Extensions:
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
Postconditions:
    New Driver's account exists with proper role
    The account can be logged into and access
    Relevant statistics/dashboard information can be accessed

## Use Case #2
Part: Duplicate account prevention
Name: User is prevented from making a new account with the same email as existing account
Primary actor: User
Stakeholders & interests: 
  1. new users: need appropriate feedback when registration fails
  2. Existing users: need protection from others using their email for another account
  3. Admin: needs errors to be handled appropriate instead of causing crashes
  4. Business: needs user accounts to be unique
Preconditions: 
  1. Frontend and Backend are running correctly
  2. An account already exists with the email the user is trying to register a new account with
  3. The user trying to register isn't already logged in
Trigger: User attempts to register a new account with an email that is already being used on another account.
Main success scenario:
    1. User accesses the user registration page
    2. User enters a new username for their desired account
    3. User enters an email that is already tied to an existing, registered account
    4. User enters password and password confirmation
    5. User selects role(driver, staff, customer)
    6. User submits registration form
    7. System detects that the email is already being used and rejects the registration attempt
    8. Frontend displays error message that the email is already being used, and that a different address must be used
Extensions:
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
Postconditions:
  1. The new account with the duplicate email is not created
  2. The old account that already used that email is unchanged
  3. Frontend provides error message informing user that registration failed due to duplicate email

## Use Case #3
Part:
Name:
Primary actor:
Stakeholders & interests:
Preconditions:
Trigger:
Main success scenario
Extensions:
Postconditions:

## Use Case #4
Part:
Name:
Primary actor:
Stakeholders & interests:
Preconditions:
Trigger:
Main success scenario:
Extensions:
Postconditions:

## Use Case #5
Part:
Name:
Primary actor:
Stakeholders & interests:
Preconditions:
Trigger:
Main success scenario:
Extensions:
Postconditions:
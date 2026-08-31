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

Use Case #1
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
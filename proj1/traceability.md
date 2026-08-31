# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |
| Use Case #2 | Main success scenario: prevent duplicate email registration and preserve original account | `test_prevents_duplicate_email_registration_and_preserves_original_account` |
| Use Case #2 | Extension 2a: username already being used with a different account | `test_rejects_duplicate_username_registration` |
| Use Case #2 | Extension 4a: password format/length validation failure | `test_rejects_registration_with_invalid_password` |
| Use Case #2 | Extension 5a: user does not select a role or missing fields | `test_rejects_incomplete_registration_missing_role` |
| Use Case #2 | Cross-role duplicate email prevention (customer email used for driver) | `test_prevents_cross_role_duplicate_email_registration` |
| Use Case #3 | Extension 2a: username already taken, rejected with a username-specific message | `test_rejects_duplicate_username_with_specific_message` |
| Use Case #3 | Extension 2b: email already tied to another account | `test_rejects_duplicate_email_registration_with_client_error` |
| Use Case #3 | Extension 2c: email entered in an invalid format | `test_rejects_invalid_email_format_with_specific_message` |
| Use Case #3 | Extension 2d: password entered in an invalid format, rejected with a password-specific message | `test_rejects_invalid_password_format_with_specific_message` |
| Use Case #3 | Extension 2f: user does not select a role | `test_rejects_missing_role_with_client_error` |
| Use Case #3 | Postconditions 1 & 2: rejected registration does not create an account | `test_invalid_registration_does_not_create_account` |
| Use Case #3 | Main success scenario step 7 & Postcondition 4: user corrects the offending field and resubmits successfully | `test_user_can_correct_and_resubmit_after_registration_error` |

Current findings:
- Use Case #1 Extension 5a & Use Case #2 Main Success Scenario / Cross-role tests, plus Use Case #3 Extension 2b, expose a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error (matching Use Case #2 Extension 7a).
- Use Case #3 Extension 2c exposes a backend defect. The email-format validation branch in `AuthServiceImpl.register` logs and returns the wrong string literal ("Username must be between 3-50 characters" instead of an email-specific message), so the frontend cannot tell the user their email was the problem.
- Use Case #3 Extension 2f exposes a backend defect. `AuthServiceImpl.register` has no explicit check for a missing role; when `role` is absent, `setCorrectRoles` calls `.toLowerCase()` on a null value, throwing a `NullPointerException` that `GlobalExceptionHandler`'s generic handler reports as HTTP 500 with a raw Java error message instead of a "select a role" validation error.


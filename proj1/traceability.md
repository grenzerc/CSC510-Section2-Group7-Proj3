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

Current findings:
- Use Case #1 Extension 5a & Use Case #2 Main Success Scenario / Cross-role tests expose a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error (matching Use Case #2 Extension 7a).


# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |

Current finding:
- Extension 5a exposes a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error.

| Use Case #11 | Main success scenario: admin promotes a customer to staff | `test_admin_can_promote_a_customer_to_staff` |
| Use Case #11 | Extension 2a: a non-admin cannot list users | `test_a_customer_cannot_list_every_user` |
| Use Case #11 | Extension 5a: role change on an unknown user id | `test_changing_the_role_of_a_user_that_does_not_exist_is_not_found` |
| Use Case #11 | Extension 5b: an invented role is rejected | `test_rejects_a_role_that_is_not_a_real_role` |
| Use Case #11 | Extension 5b: an empty role is rejected | `test_rejects_an_empty_role` |
| Use Case #11 | Extension 4a: registering with an unrecognized role is rejected | `test_registering_with_an_unknown_role_is_rejected` |
| Use Case #11 | Extension 5c: the last admin cannot be demoted (written, not run) | `test_the_last_admin_cannot_be_demoted` |

# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |

Current finding:
- Extension 5a exposes a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error.


| Use Case #2 | Main success scenario: authenticated customer updates cost and dietary preferences | `test_customer_can_update_food_preferences` |
| Use Case #2 | Postcondition: updated preferences persist and can be retrieved | `test_updated_food_preferences_are_returned_in_customer_profile` |
| Use Case #2 | Extension 3a: unsupported cost preference is rejected | `test_rejects_unsupported_cost_preference` |
| Use Case #2 | Extension 3b: customer selects no dietary restrictions | `test_customer_can_save_preferences_without_dietary_restrictions` |

Current Finding:
- Use Case #2 exposes missing server-side cost-preference validation. The frontend offers only `budget`, `moderate`, `premium`, and `no-limit`, but the backend accepts and persists an unsupported value and returns HTTP 200.
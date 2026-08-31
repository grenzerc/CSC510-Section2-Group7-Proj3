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

| Use Case #12 | Main success scenario: staff reads the inventory | `test_staff_can_read_the_inventory` |
| Use Case #12 | Extension 2a: the inventory requires a login | `test_the_inventory_cannot_be_read_without_logging_in` |
| Use Case #12 | Extension 4a: a customer cannot rewrite the inventory | `test_a_customer_cannot_rewrite_the_inventory` |
| Use Case #12 | Extension 4b: a driver cannot add a menu item | `test_a_driver_cannot_add_a_menu_item` |
| Use Case #12 | Extension 4b: a customer cannot delete a menu item | `test_a_customer_cannot_delete_a_menu_item` |
| Use Case #12 | Extension 4c: a negative price is rejected | `test_rejects_a_negative_price` |
| Use Case #12 | Extension 4e: a duplicate food name is rejected | `test_rejects_a_duplicate_food_name` |

| Use Case #13 | Main success scenario: a driver reads their own statistics | `test_a_driver_can_read_their_own_statistics` |
| Use Case #13 | Extension 2a: statistics require a login | `test_driver_statistics_require_a_login` |
| Use Case #13 | Extension 2b: one driver cannot read another's statistics | `test_one_driver_cannot_read_another_drivers_statistics` |
| Use Case #13 | Extension 2b: a customer cannot read driver statistics | `test_a_customer_cannot_read_driver_statistics` |
| Use Case #13 | Extension 2c: an unknown driver username is not found | `test_an_unknown_username_is_not_found` |

| Use Case #14 | Precondition: a customer saves budget and dietary preferences | `test_a_customer_can_save_a_budget_and_a_restriction` |
| Use Case #14 | Extension 4a (exact match): a matching allergen hides the food | `test_an_exactly_worded_restriction_hides_the_food` |
| Use Case #14 | Extension 4a (plural): "peanuts" does not match "peanut" | `test_a_plural_restriction_still_hides_the_food` |
| Use Case #14 | Extension 4a (category): "nuts" does not match "tree nuts" | `test_a_broader_restriction_still_hides_the_food` |
| Use Case #14 | Extension 3b: the premium tier hides food above $35 | `test_premium_customers_can_see_the_whole_menu` |
| Use Case #14 | Extension 5a: the food API applies no preference filtering | `test_the_food_api_applies_no_preferences_of_its_own` |

| Use Case #15 | Authentication is required to use the assistant | `test_the_assistant_cannot_be_used_without_logging_in` |
| Use Case #15 | Extension 1a: a driver cannot use the assistant | `test_a_driver_cannot_use_the_assistant` |
| Use Case #15 | Main success scenario: the assistant answers a greeting (requires Ollama running) | `test_the_assistant_answers_a_greeting` |
| Use Case #15 | Extension 4a: an unreachable model is reported as a failure | `test_an_unreachable_model_is_reported_as_a_failure` |

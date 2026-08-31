# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |

Current finding:
- Extension 5a exposes a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error.

| Use Case #16 | Main success scenario: authenticated customer updates food preferences | `test_customer_can_update_food_preferences` |
| Use Case #16 | Success postcondition: updated preferences persist | `test_updated_food_preferences_are_returned_in_customer_profile` |
| Use Case #16 | Extension 3a: unsupported cost preference is rejected | `test_rejects_unsupported_cost_preference` |
| Use Case #16 | Extension 3b: customer selects no dietary restrictions | `test_customer_can_save_preferences_without_dietary_restrictions` |
| Use Case #17 | Main success scenario: authenticated customer retrieves food inventory | `test_authenticated_customer_can_browse_food_inventory` |
| Use Case #17 | Displayed information: foods contain inventory-page information | `test_inventory_foods_contain_displayed_information` |
| Use Case #17 | Extension 1a: unauthenticated inventory request is rejected | `test_rejects_unauthenticated_food_inventory_request` |
| Use Case #17 | Success postcondition: browsing does not change inventory | `test_browsing_food_inventory_does_not_change_inventory` |
| Use Case #18 | Main success scenario: authenticated customer creates a food order | `test_authenticated_customer_can_create_food_order` |
| Use Case #18 | Success postcondition: created order appears in personal orders | `test_created_order_appears_in_customer_orders` |
| Use Case #18 | Extension 7a: backend rejects an order without food | `test_rejects_order_without_food` |
| Use Case #18 | Extension 4a: backend rejects quantity above available stock | `test_rejects_order_quantity_above_available_stock` |
| Use Case #19 | Main success scenario: customer retrieves personal orders | `test_customer_can_view_personal_orders` |
| Use Case #19 | Extension 2b: another customer's order is excluded | `test_personal_orders_do_not_include_another_customers_order` |
| Use Case #19 | Extension 2a: new customer receives an empty order list | `test_new_customer_receives_empty_personal_order_list` |
| Use Case #19 | Extension 3a: repeated food entries are preserved | `test_personal_order_details_preserve_repeated_food_entries` |
| Use Case #20 | Main success scenario: customer rates food from a fulfilled order | `test_customer_can_rate_food_from_fulfilled_order` |
| Use Case #20 | Extension 6a: duplicate rating is rejected | `test_rejects_duplicate_rating_for_same_food_and_order` |
| Use Case #20 | Extension 2a: food from an unfulfilled order cannot be rated | `test_rejects_rating_food_from_unfulfilled_order` |
| Use Case #20 | Extension 6b: another customer cannot rate the order | `test_rejects_rating_another_customers_order` |

## Current Findings

- Use Case #16: The backend accepts and persists unsupported cost-preference values.
- Use Case #17: All tested inventory retrieval and access-control behavior passes.
- Use Case #18: The backend accepts empty orders and orders exceeding available stock.
- Use Case #19: All tested personal-order retrieval and account-isolation behavior passes.
- Use Case #20: The backend allows an authenticated customer to rate another customer's fulfilled order.

]
# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |
| Use Case #6 | Main success scenario + Postconditions: fulfill an order, confirm it appears in `/api/orders/fulfilledOrders` and the owning customer's `/my-orders/fulfilled` | `test_fulfilling_an_order_updates_status_and_both_order_lists` |
| Use Case #6 | Extension 2a: order id does not exist, rejected with 412 | `test_fulfilling_a_nonexistent_order_returns_412` |
| Use Case #6 | Extension 2b: order is already fulfilled, rejected with 410 | `test_fulfilling_an_already_fulfilled_order_returns_410` |
| Use Case #7 | Main success scenario: admin deletes an ordinary user and their orders, admin count unaffected | `test_admin_deletes_an_ordinary_user_and_their_orders` |
| Use Case #7 | Extension 2a: admin deletes their own account (documents current behavior — passes) | `test_an_admin_can_delete_their_own_account` |
| Use Case #7 | Extension 2a: admin account should survive a self-delete attempt (asserts correct behavior — currently FAILS) | `test_an_admin_should_not_be_able_to_delete_their_own_account` |
| Use Case #7 | Extension 2b: deleting a non-existent user | `test_deleting_a_nonexistent_user_returns_200_instead_of_404` |
| Use Case #7 | Extension 5a: deleting a user with placed orders | `test_deleting_a_user_with_orders_deletes_their_orders_too` |
| Use Case #7 | Extension 5b: deleting a driver account | `test_deleting_a_driver_leaves_driver_stats_orphaned` |
| Use Case #7 | Extension 5c: deleting the last remaining admin (written, not run — see finding below) | `test_the_last_remaining_admin_cannot_be_deleted` |
| Use Case #8 | Main success scenario: staff adds a food item | `test_staff_can_add_a_food_item` |
| Use Case #8 | Extension 2a: food should not actually be created by a non-Admin/Staff account (asserts correct behavior — currently FAILS) | `test_customer_should_not_be_able_to_add_a_food_item` |
| Use Case #9 | Extension 4a: item appears in at least one unfulfilled order | `test_deletion_is_blocked_while_an_unfulfilled_order_contains_the_item` |
| Use Case #9 | Extension 1a: customer's delete request should be rejected at the authorization layer (asserts correct behavior — currently FAILS, and fails worse than expected — see finding below) | `test_customer_should_not_be_able_to_delete_a_food_item` |
| Use Case #9 | Extension 5a: deleting a food in a fulfilled order (live environment cannot reach this state — see finding below) | `test_deleting_a_food_in_a_fulfilled_order_fails_before_reaching_extension_5a` |
| Use Case #9 | Extension 5b: deleting a rated food (live environment cannot reach this state — see finding below) | `test_deleting_a_rated_food_also_fails_before_reaching_extension_5b` |
| Use Case #10 | Main success scenario: a driver picks up then delivers an order, earnings credited exactly once | `test_a_driver_can_pick_up_and_deliver_an_order` |
| Use Case #10 | Extension 2b: order already assigned to another driver, or already "Picked Up" | `test_any_driver_can_pick_up_an_order_already_assigned_to_another_driver` |
| Use Case #10 | Extension 5a: "Delivered" submitted by a driver who is NOT the order's assigned driver | `test_delivered_by_the_wrong_driver_leaves_the_order_unfulfilled` |
| Use Case #10 | Extension 5b: order's driver is still unassigned when "Delivered" arrives | `test_delivering_an_order_with_no_assigned_driver_crashes` |
| Use Case #10 | Extension 5c: status value is missing | `test_a_missing_status_value_crashes` |
| Use Case #10 | Extension 5d: status value is an unrecognized string | `test_an_unrecognized_status_value_is_accepted` |
| Use Case #10 | Extension 5e: already-delivered order receives a second "Delivered" call (documents current behavior — passes) | `test_a_second_delivered_call_double_credits_earnings` |
| Use Case #10 | Extension 5e: earnings should not be credited again on a second "Delivered" call (asserts correct behavior — currently FAILS) | `test_a_second_delivered_call_should_not_double_credit_earnings` |
| Use Case #10 | Extension 5f: stale "Pick Up" click lands on an already-delivered order | `test_a_stale_pickup_reverts_an_already_delivered_order` |

Current finding:
- Extension 5a exposes a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error.

Current findings (Use Cases #6-#10):
- Use Case #7, Extension 2a: `UserServiceImpl.deleteUser()` (lines 55-71) has no self-delete check — the guard exists only in `UserManagement.js`. An admin can delete their own account via a direct API call.
- Use Case #7, Extension 2b: deleting a non-existent user ID returns 200 OK instead of 404 — `deleteUser()` (lines 59-61) returns silently when the user isn't found.
- Use Case #7, Extension 5b: `DriverStats` has no foreign key back to `User`; deleting a driver's account leaves their stats row permanently orphaned.
- Use Case #7, Extension 5c: no check anywhere prevents deleting the last remaining admin, leaving the platform with zero admins and no in-app recovery path.
- Use Cases #8/#9, Extensions 2a/1a: `FoodController` has no `@PreAuthorize` on `createFood()` or `deleteFood()`, and neither endpoint is restricted in `SpringSecurityConfig` — any authenticated account, regardless of role, can create or delete catalog items.
- Use Case #9, Extension 5a: `FoodServiceImpl.deleteFood()` (lines 166-172) silently strips a deleted food from every fulfilled order's item list but never recomputes `Order.cost`/`deliveryCost` — price and item list become permanently inconsistent. Confirmed via the JUnit suite in an isolated database (`testDeleteFood_removesItemFromFulfilledOrder_priceStaysStale`).
- Use Case #9, Extension 5b: `deleteFood()` never touches `Order.ratedFoodIds` — a rating recorded against a food survives as a dangling reference after the food is deleted. Confirmed via the JUnit suite in an isolated database (`testDeleteFood_ratingRecordStillReferencesDeletedItem`).
- Use Case #9, new finding from the pytest suite: against the live, persistent database, `DELETE /api/foods/{id}` fails with an unhandled 500 for *any* food that was ever added through the normal creation path, for *any* caller, admin included — `deleteFood()` never removes the food from `Inventory.foods` before deleting the row, so MySQL's FK constraint on `inventory_foods` blocks it every time. This is more severe than the authorization gap alone: even the legitimate admin path is broken. It also means the live pytest suite cannot reach the states extensions 5a/5b describe (deletion never succeeds), while the JUnit suite can, because `@BeforeEach` wipes the Inventory row entirely each test. Independently corroborated against Use Case #12's own `test_a_customer_cannot_delete_a_menu_item`, whose docstring predicts this exact failure.
- Use Case #10, Extensions 5b/5c: `OrderServiceImpl.updateOrder()` (lines 274, 278) has no null-checks on `status` or `order.getDriver()`, causing unhandled `NullPointerException`s that surface as 500 errors.
- Use Case #10, Extension 5e: `DriverStatsImpl.updateTotalEarnings()` (lines 46-47) is called unconditionally on every "Delivered" transition with no check on `order.getIsFulfilled()` — reprocessing an already-delivered order double-credits both earnings and delivery count.
- Use Case #10, Extension 5f: a stale "Pick Up" call on an already-delivered order silently reverts `isFulfilled` to false (lines 281-283), while previously-credited earnings are never clawed back — leaving no way to reconcile the mismatch through the app.



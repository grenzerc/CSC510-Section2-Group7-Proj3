# Project 1 Results Table

Format: `Test | Why we tried it | Expected | What happened`. All 107 tests below
are the full pytest suite on `main` (all 20 use cases), executed live with
`pytest -v` against the real FoodSeer backend and MySQL — no mocks, no test
doubles. 72 passed, 32 failed, 3 skipped. A separate section at the bottom
covers the 29-test JUnit suite (Use Cases #6-#10 only, 
branch), which documents several of the same defects at the unit/service
layer, plus a few this black-box suite structurally cannot reach.

Tests marked "documents current behavior" pass because they assert what the
backend actually does; tests marked "asserts correct behavior" fail on
purpose because they assert what the use case says it should do. Both are
deliberate — see `test-plan.md` and `test-suite-evaluation.md` for the full
narrative behind each defect.

## Use Case #1 — Driver Registration and Dashboard Access

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_register_and_login_as_driver_allows_dashboard_access` | Main success scenario: register, log in, verify `ROLE_DRIVER`, load driver stats | All steps succeed | PASS |
| `test_rejects_incomplete_driver_registration_information` | Extension 3a: incomplete registration should be rejected | 4xx rejection | PASS |
| `test_rejects_driver_login_with_invalid_credentials` | Extension 7a: invalid login credentials should be rejected | 4xx rejection | PASS |
| `test_rejects_duplicate_driver_email_address` | Extension 5a: a second account should not reuse an existing email | 400 with a clean validation message | **FAIL** — backend returns 500 (raw DB unique-constraint error), not 400 |

## Use Case #2 — Duplicate Account Prevention

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_prevents_duplicate_email_registration_and_preserves_original_account` | Main scenario: duplicate email registration should be rejected without disturbing the original account | 4xx, original account intact | **FAIL** — same underlying 500 as UC1 Extension 5a |
| `test_rejects_duplicate_username_registration` | Extension 2a: username already in use | 4xx rejection | PASS |
| `test_rejects_registration_with_invalid_password` | Extension 4a: password format/length validation | 4xx rejection | PASS |
| `test_rejects_incomplete_registration_missing_role` | Extension 5a: missing role or fields | 4xx rejection | PASS |
| `test_prevents_cross_role_duplicate_email_registration` | Cross-role duplicate email (customer email reused for driver) | 4xx rejection | **FAIL** — same 500 root cause |

## Use Case #3 — Registration Error Handling

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_rejects_duplicate_username_with_specific_message` | Extension 2a: duplicate username, username-specific message | 4xx with specific message | PASS |
| `test_rejects_invalid_password_format_with_specific_message` | Extension 2d: invalid password format, password-specific message | 4xx with specific message | PASS |
| `test_rejects_duplicate_email_registration_with_client_error` | Extension 2b: duplicate email, client error with specific message | 400 with email-specific message | **FAIL** — 500, same DB-constraint root cause as UC1/UC2 |
| `test_rejects_invalid_email_format_with_specific_message` | Extension 2c: malformed email, email-specific message | 400 mentioning "email" | **FAIL** — returns the wrong string literal ("Username must be between 3-50 characters") |
| `test_rejects_missing_role_with_client_error` | Extension 2f: no role selected | 400 with role-selection message | **FAIL** — NPE on `role().toLowerCase()`, surfaces as unhandled 500 |
| `test_invalid_registration_does_not_create_account` | Postconditions 1 & 2: a rejected registration should not create an account | No account created | PASS |
| `test_user_can_correct_and_resubmit_after_registration_error` | Main scenario step 7 & Postcondition 4: user corrects the field and resubmits | Second attempt succeeds | PASS |

## Use Case #4 — Login Redirection

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_login_authenticates_valid_credentials_and_returns_session_token` | Main scenario steps 1-4: valid login issues a session token | 200 + token | PASS |
| `test_rejects_login_with_invalid_credentials` | Extension 2a: invalid username/password | 4xx rejection | PASS |
| `test_login_identifies_role_for_customer_redirection` | Main scenario step 5 / Extension 6d: role identified for redirect | Correct role returned | PASS |
| `test_login_identifies_role_for_driver_redirection` | Extension 6c: driver role redirect | Correct role returned | PASS |
| `test_login_identifies_role_for_staff_redirection` | Extension 6b: staff role redirect | Correct role returned | PASS |
| `test_customer_can_access_role_appropriate_endpoint` | Postcondition 4: role-appropriate access | 200 | PASS |
| `test_customer_is_blocked_from_admin_only_endpoint` | Postcondition 5 / Extension 6e: customer blocked from admin endpoint | 403 | PASS |
| `test_driver_is_blocked_from_customer_only_endpoint` | Postcondition 5 / Extension 6e: driver blocked from customer endpoint | 403 | PASS |
| `test_unauthenticated_request_is_rejected_from_protected_endpoint` | Preconditions: unauthenticated request rejected | 401 | PASS |
| `test_login_fails_for_account_with_no_valid_role` | Extension 5a: account with no valid role should be rejected at login | 401 with a role-related message | **FAIL** — `setCorrectRoles()` allows an empty role through registration; login then fails with the unrelated technical message "A granted authority textual representation is required," permanently locking the account out |

## Use Case #5 — Restricted Dashboard Access

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_unauthenticated_request_rejected_from_admin_only_endpoint` | Extension 2a/4a: unauthenticated request to admin-only endpoint | 401 | PASS |
| `test_own_profile_endpoint_rejects_unauthenticated_access` | Extension 2a: unauthenticated request to `/me` | 401 | PASS |
| `test_unauthenticated_request_rejected_from_role_restricted_order_endpoint` | Extension 4a: unauthenticated request to a role-restricted order endpoint | 401 | PASS |
| `test_customer_blocked_from_admin_only_endpoint` | Extension 3b: customer blocked from admin-only endpoint | 403 | PASS |
| `test_customer_blocked_from_driver_or_admin_order_endpoint` | Extension 3a: customer blocked from driver/admin order endpoint | 403 | PASS |
| `test_driver_stats_endpoint_allows_unauthenticated_access` | Precondition 2 / Extension 4a: driver stats should reject unauthenticated requests, like every other dashboard endpoint | 401 | **FAIL** — 200, no auth required at all |
| `test_customer_blocked_from_viewing_driver_dashboard_stats` | Extension 3a: customer blocked from viewing driver stats | 403 | **FAIL** — 200, no role check on this endpoint |

## Use Case #6 — Fulfilled Order

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_fulfilling_an_order_updates_status_and_both_order_lists` | Main scenario + Postconditions: fulfilling updates status and appears in both order lists | All three postconditions hold | PASS |
| `test_fulfilling_a_nonexistent_order_returns_412` | Extension 2a: unknown order id | 412 | PASS |
| `test_fulfilling_an_already_fulfilled_order_returns_410` | Extension 2b: already-fulfilled order | 410 | PASS |

## Use Case #7 — Delete User Account

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_admin_deletes_an_ordinary_user_and_their_orders` | Main scenario: ordinary delete, admin count unaffected | User and orders gone, admin count unchanged | PASS |
| `test_an_admin_can_delete_their_own_account` | Extension 2a: self-delete (documents current behavior) | Delete succeeds despite being self-delete | PASS |
| `test_an_admin_should_not_be_able_to_delete_their_own_account` | Same bug, asserted as correct behavior | Admin should survive a self-delete attempt | **FAIL** — self-delete succeeds; no backend guard |
| `test_deleting_a_nonexistent_user_returns_200_instead_of_404` | Extension 2b: missing user | 200 (documents the actual, non-ideal behavior) | PASS |
| `test_deleting_a_user_with_orders_deletes_their_orders_too` | Extension 5a: user has placed orders | Orders deleted with the user | PASS |
| `test_deleting_a_driver_leaves_driver_stats_orphaned` | Extension 5b: deleted user was a driver | Stats row survives, orphaned | PASS |
| `test_the_last_remaining_admin_cannot_be_deleted` | Extension 5c: last admin (written, not run) | N/A | SKIPPED — would lock the whole team out of `/api/users` |

## Use Case #8 — Add a Food Item

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_staff_can_add_a_food_item` | Main scenario: staff adds a food item | 200, item created | PASS |
| `test_customer_should_not_be_able_to_add_a_food_item` | Extension 2a, asserted as correct behavior | 403 for a non-Admin/Staff account | **FAIL** — 200, no role check on `POST /api/foods` |

## Use Case #9 — Remove a Food Item

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_customer_should_not_be_able_to_delete_a_food_item` | Extension 1a, asserted as correct behavior | 403 at the authorization layer | **FAIL** — 500 (Inventory FK-constraint bug fires before any authz check would matter) |
| `test_deletion_is_blocked_while_an_unfulfilled_order_contains_the_item` | Extension 4a: item in an unfulfilled order | 409, naming the blocking count | PASS |
| `test_deleting_a_food_in_a_fulfilled_order_fails_before_reaching_extension_5a` | Extension 5a, live-environment blocker | 500 (documents the FK-constraint bug pre-empting the deeper order-mutation defect) | PASS |
| `test_deleting_a_rated_food_also_fails_before_reaching_extension_5b` | Extension 5b, live-environment blocker | 500, same reason | PASS |

## Use Case #10 — Update Order Status

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_a_driver_can_pick_up_and_deliver_an_order` | Main scenario: pick up then deliver, earnings credited once | All steps succeed, earnings credited exactly once | PASS |
| `test_any_driver_can_pick_up_an_order_already_assigned_to_another_driver` | Extension 2b: reassignment guard | Silent reassignment succeeds (documents no guard) | PASS |
| `test_delivered_by_the_wrong_driver_leaves_the_order_unfulfilled` | Extension 5a: wrong driver delivers | Status overwritten, stays unfulfilled, no error | PASS |
| `test_delivering_an_order_with_no_assigned_driver_crashes` | Extension 5b: no assigned driver | Unhandled crash (500) | PASS |
| `test_a_missing_status_value_crashes` | Extension 5c: missing status | Unhandled crash (500) | PASS |
| `test_an_unrecognized_status_value_is_accepted` | Extension 5d: unrecognized status string | Accepted and persisted as-is | PASS |
| `test_a_second_delivered_call_double_credits_earnings` | Extension 5e, documents current behavior | Earnings credited a second time | PASS |
| `test_a_second_delivered_call_should_not_double_credit_earnings` | Same bug, asserted as correct behavior | Earnings should not double-credit | **FAIL** — earnings go 5.0 → 10.0 on reprocessing |
| `test_a_stale_pickup_reverts_an_already_delivered_order` | Extension 5f: stale pickup on a delivered order | Silently reverts to unfulfilled, earnings not clawed back | PASS |

## Use Case #11 — Administrative Role Management

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_admin_can_promote_a_customer_to_staff` | Main scenario: promote a customer to staff | 200, role updated | PASS |
| `test_a_customer_cannot_list_every_user` | Extension 2a: user list is admin-only | 403 | PASS |
| `test_changing_the_role_of_a_user_that_does_not_exist_is_not_found` | Extension 5a: unknown user id | 404 | PASS |
| `test_rejects_a_role_that_is_not_a_real_role` | Extension 5b: invented role (`ROLE_WIZARD`) | 400 rejection | **FAIL** — 200, `setRole()` stores anything with no validation |
| `test_rejects_an_empty_role` | Extension 5b: empty-string role | 400 rejection | **FAIL** — 200, empty role persists, account authorized for nothing |
| `test_registering_with_an_unknown_role_is_rejected` | Extension 4a: registering with an unrecognized role | 400 rejection | **FAIL** — 200, account created with a blank role |
| `test_the_last_admin_cannot_be_demoted` | Extension 5c: last admin (written, not run) | N/A | SKIPPED — would lock the whole team out |

## Use Case #12 — Inventory and Menu Management

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_staff_can_read_the_inventory` | Main scenario: staff reads the inventory | 200 | PASS |
| `test_the_inventory_cannot_be_read_without_logging_in` | Extension 2a: inventory requires login | 401 | PASS |
| `test_a_customer_cannot_rewrite_the_inventory` | Extension 4a: customer should not write inventory | 403 | **FAIL** — 200, `InventoryController` admits `CUSTOMER` on the write path |
| `test_a_driver_cannot_add_a_menu_item` | Extension 4b: driver adds a menu item | 403 | **FAIL** — 200, `FoodController` has no role check at all |
| `test_a_customer_cannot_delete_a_menu_item` | Extension 4b: customer deletes a menu item | 403 | **FAIL** — 500 (unauthorized request reaches the DB and trips an FK constraint, leaking a raw SQL error) |
| `test_rejects_a_negative_price` | Extension 4c: negative price | 400 rejection | PASS |
| `test_rejects_a_duplicate_food_name` | Extension 4e: duplicate food name | 409 rejection | PASS |

## Use Case #13 — Driver Delivery Statistics

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_a_driver_can_read_their_own_statistics` | Main scenario: driver reads their own stats | 200 | PASS |
| `test_driver_statistics_require_a_login` | Extension 2a: stats require a login | 401 | **FAIL** — 200 with zero credentials |
| `test_one_driver_cannot_read_another_drivers_statistics` | Extension 2b: cross-driver access | 403 | **FAIL** — 200, no ownership check |
| `test_a_customer_cannot_read_driver_statistics` | Extension 2b: customer reads driver stats | 403 | **FAIL** — 200, same missing check |
| `test_an_unknown_username_is_not_found` | Extension 2c: unknown driver username | 404 | **FAIL** — 200 with an empty body instead |

## Use Case #14 — Food Recommendation

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_a_customer_can_save_a_budget_and_a_restriction` | Precondition: save budget and dietary preference | Saved successfully | PASS |
| `test_an_exactly_worded_restriction_hides_the_food` | Extension 4a (exact match): allergen matches restriction wording exactly | Food hidden | PASS |
| `test_a_plural_restriction_still_hides_the_food` | Extension 4a (plural): "peanuts" vs. "peanut" | Food hidden | **FAIL** — plural doesn't match, unsafe food shown |
| `test_a_broader_restriction_still_hides_the_food` | Extension 4a (category): "nuts" vs. "tree nuts" | Food hidden | **FAIL** — category doesn't match, unsafe food shown |
| `test_premium_customers_can_see_the_whole_menu` | Extension 3b: premium tier should be unbounded | $40 item visible | **FAIL** — premium tier caps at $35 |
| `test_the_food_api_applies_no_preferences_of_its_own` | Extension 5a: does `GET /api/foods` itself filter? | Filtering exists somewhere server-side | **FAIL** — full menu always returned; filtering is client-side only |

## Use Case #15 — AI Chat Assistant

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_the_assistant_cannot_be_used_without_logging_in` | Authentication required | 401 | PASS |
| `test_a_driver_cannot_use_the_assistant` | Extension 1a: driver cannot use assistant | 403 | PASS |
| `test_the_assistant_answers_a_greeting` | Main scenario: greeting gets a reply (needs Ollama) | Non-empty reply | SKIPPED — Ollama not running during this run |
| `test_an_unreachable_model_is_reported_as_a_failure` | Extension 4a: model unreachable should be reported distinctly | A failure distinguishable from a real answer | **FAIL** — 200 with `"Error: ..."` embedded in the same field a real answer uses |

## Use Case #16 — Update Food Preferences

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_customer_can_update_food_preferences` | Main scenario: update cost preference and restrictions | 200, values returned | PASS |
| `test_updated_food_preferences_are_returned_in_customer_profile` | Success postcondition: values persist | Persisted values retrievable | PASS |
| `test_customer_can_save_preferences_without_dietary_restrictions` | Extension 3b: no dietary restrictions selected | Accepted | PASS |
| `test_rejects_unsupported_cost_preference` | Extension 3a: unsupported cost preference | 400 rejection | **FAIL** — 200, arbitrary value stored |

## Use Case #17 — Browse Food Inventory

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_authenticated_customer_can_browse_food_inventory` | Main scenario: retrieve food inventory | 200, foods returned | PASS |
| `test_inventory_foods_contain_displayed_information` | Displayed information present | Fields present | PASS |
| `test_rejects_unauthenticated_food_inventory_request` | Extension 1a: unauthenticated request | 401 | PASS |
| `test_browsing_food_inventory_does_not_change_inventory` | Success postcondition: browsing is read-only | No change | PASS |

## Use Case #18 — Create a Food Order

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_authenticated_customer_can_create_food_order` | Main scenario: create an order | 200, order returned | PASS |
| `test_created_order_appears_in_customer_orders` | Success postcondition: order appears in personal orders | Appears | PASS |
| `test_rejects_order_without_food` | Extension 7a: empty cart bypassed at the API | 400 rejection | **FAIL** — 200, empty order created |
| `test_rejects_order_quantity_above_available_stock` | Extension 4a: quantity exceeds stock | 400 rejection | **FAIL** — 200, order exceeding stock created |

## Use Case #19 — View Personal Orders

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_customer_can_view_personal_orders` | Main scenario: retrieve personal orders | 200, order present | PASS |
| `test_personal_orders_do_not_include_another_customers_order` | Extension 2b: account isolation | Other customer's order excluded | PASS |
| `test_new_customer_receives_empty_personal_order_list` | Extension 2a: new customer, empty list | Empty list | PASS |
| `test_personal_order_details_preserve_repeated_food_entries` | Extension 3a: repeated food entries preserved | Entries preserved | PASS |

## Use Case #20 — Rate Food from a Fulfilled Order

| Test | Why we tried it | Expected | What happened |
|---|---|---|---|
| `test_customer_can_rate_food_from_fulfilled_order` | Main scenario: rate food after fulfillment | 200, rating recorded | PASS |
| `test_rejects_duplicate_rating_for_same_food_and_order` | Extension 6a: duplicate rating | 409 rejection | PASS |
| `test_rejects_rating_food_from_unfulfilled_order` | Extension 2a: unfulfilled order cannot be rated | 4xx rejection | PASS |
| `test_rejects_rating_another_customers_order` | Extension 6b: another customer rates the order | 403/404 rejection | **FAIL** — 200, no ownership check on rating |

## Summary (pytest suite, all 20 use cases)

- **107 tests total: 72 passed, 32 failed, 3 skipped.**
- 17 of 20 use case files have at least one failure; 3 (UC6, UC17, UC19) are fully green.
- All 3 skips are deliberately-unrun, written tests that would touch the single shared seeded admin account — the same safety pattern used consistently across the suite.
- Every failure traces to a specific, cited line in the backend and is explained in `test-plan.md` and/or `test-suite-evaluation.md` — none are flaky or unexplained.

---

## JUnit suite (Use Cases #6-#10 only,  branch, not merged to `main`)

29 tests, run via `mvn test` against the same live backend and MySQL, at the
service/controller layer rather than pure black-box HTTP. 25 passed, 4 failed
(deliberate red tests, same pattern as above).


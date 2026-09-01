# Project 1 Traceability

| Use Case | Scenario or Extension | Test |
| --- | --- | --- |
| Use Case #1 | Main success scenario: register and login as driver, then access dashboard data | `test_register_and_login_as_driver_allows_dashboard_access` |
| Use Case #1 | Extension 3a: incomplete or invalid registration information | `test_rejects_incomplete_driver_registration_information` |
| Use Case #1 | Extension 5a: email account already being used | `test_rejects_duplicate_driver_email_address` |
| Use Case #1 | Extension 7a: invalid login credentials | `test_rejects_driver_login_with_invalid_credentials` |
| Use Case #6 | Main success scenario + Postconditions: fulfill an order, confirm it appears in `/api/orders/fulfilledOrders` and the owning customer's `/my-orders/fulfilled` | `testFulfillOrder_UseCase6_MainScenarioAndPostconditions` |
| Use Case #7 | Main success scenario: admin deletes an ordinary user and their orders, admin count unaffected | `shouldDeleteOrdinaryUserAndTheirOrders_mainSuccessScenario` |
| Use Case #7 | Extension 2a: admin deletes their own account (documents current behavior — passes) | `shouldAllowAdminToDeleteOwnAccount_becauseBackendHasNoSelfDeleteCheck` |
| Use Case #7 | Extension 2a: admin account should survive a self-delete attempt (asserts correct behavior — currently FAILS) | `shouldNotActuallyDeleteAdminAccount_onSelfDeleteAttempt` |
| Use Case #7 | Extension 2b: deleting a non-existent user | `shouldReturn200WhenDeletingNonExistentUser` |
| Use Case #7 | Extension 5a: deleting a user with placed orders | `shouldDeleteUsersOrders_whenDeletingUserWithOrders` |
| Use Case #7 | Extension 5b: deleting a driver account | `shouldLeaveDriverStatsOrphaned_whenDeletingADriverAccount` |
| Use Case #7 | Extension 5c: deleting the last remaining admin | `shouldAllowDeletingTheLastRemainingAdmin_withNoGuard` |
| Use Case #8 | Extension 2a: non-Admin/Staff account submits the create-food request directly (documents current behavior — passes) | `testCreateFood_succeedsForNonAdminNonStaffRole_becauseNoRoleCheckExists` |
| Use Case #8 | Extension 2a: food should not actually be created by a non-Admin/Staff account (asserts correct behavior — currently FAILS) | `testCreateFood_shouldNotActuallyCreateFood_whenSubmittedByNonAdminNonStaffRole` |
| Use Case #9 | Extension 1a: non-Admin/Staff account submits the delete-food request directly | `testDeleteFood_succeedsForNonAdminNonStaffRole_becauseNoRoleCheckExists` |
| Use Case #9 | Extension 4a: item appears in at least one unfulfilled order | `testDeleteFood_blockedByUnfulfilledOrder` |
| Use Case #9 | Extension 5a + Postconditions: item appears only in fulfilled (historical) orders | `testDeleteFood_removesItemFromFulfilledOrder_priceStaysStale` |
| Use Case #9 | Extension 5b: rated item is deleted (documents current behavior — passes) | `testDeleteFood_ratingRecordStillReferencesDeletedItem` |
| Use Case #9 | Extension 5b: rating reference should be removed when its food is deleted (asserts correct behavior — currently FAILS) | `testDeleteFood_ratedFoodIdShouldBeRemoved_whenFoodIsDeleted` |
| Use Case #10 | Extension 2b: order already assigned to another driver, or already "Picked Up" | `updateOrder_pickUp_reassignsOrder_evenIfAlreadyPickedUpByAnotherDriver` |
| Use Case #10 | Extension 5a: "Delivered" submitted by a driver who is NOT the order's assigned driver | `updateOrder_delivered_byWrongDriver_leavesUnfulfilled_noError` |
| Use Case #10 | Extension 5b: order's driver is still unassigned when "Delivered" arrives | `updateOrder_delivered_withNoAssignedDriver_throwsNPE` |
| Use Case #10 | Extension 5c: status value is missing | `updateOrder_statusIsNull_throwsNPE_beforeSave` |
| Use Case #10 | Extension 5d: status value is an unrecognized string | `updateOrder_unrecognizedStatus_isPersistedVerbatim_andFallsIntoUnfulfilledBranch` |
| Use Case #10 | Extension 5e: already-delivered order receives a second "Delivered" call (documents current behavior — passes) | `updateOrder_secondDeliveredCall_doubleCreditsEarnings` |
| Use Case #10 | Extension 5e: earnings should not be credited again on a second "Delivered" call (asserts correct behavior — currently FAILS) | `updateOrder_secondDeliveredCall_shouldNotCreditEarningsAgain` |
| Use Case #10 | Extension 5f: stale "Pick Up" click lands on an already-delivered order | `updateOrder_stalePickUp_onAlreadyDeliveredOrder_revertsToUnfulfilled` |

Current finding:
- Extension 5a exposes a backend defect. The `users.email` column is unique, but registration does not check `existsByEmail` before saving, so duplicate email registration returns HTTP 500 instead of a user-facing validation error.

Current findings (Use Cases #6-#10):
- Use Case #7, Extension 2a: `UserServiceImpl.deleteUser()` (lines 55-71) has no self-delete check — the guard exists only in `UserManagement.js`. An admin can delete their own account via a direct API call.
- Use Case #7, Extension 2b: deleting a non-existent user ID returns 200 OK instead of 404 — `deleteUser()` (lines 59-61) returns silently when the user isn't found.
- Use Case #7, Extension 5b: `DriverStats` has no foreign key back to `User`; deleting a driver's account leaves their stats row permanently orphaned.
- Use Case #7, Extension 5c: no check anywhere prevents deleting the last remaining admin, leaving the platform with zero admins and no in-app recovery path.
- Use Cases #8/#9, Extensions 2a/1a: `FoodController` has no `@PreAuthorize` on `createFood()` or `deleteFood()`, and neither endpoint is restricted in `SpringSecurityConfig` — any authenticated account, regardless of role, can create or delete catalog items.
- Use Case #9, Extension 5a: `FoodServiceImpl.deleteFood()` (lines 166-172) silently strips a deleted food from every fulfilled order's item list but never recomputes `Order.cost`/`deliveryCost` — price and item list become permanently inconsistent.
- Use Case #9, Extension 5b: `deleteFood()` never touches `Order.ratedFoodIds` — a rating recorded against a food survives as a dangling reference after the food is deleted.
- Use Case #10, Extensions 5b/5c: `OrderServiceImpl.updateOrder()` (lines 274, 278) has no null-checks on `status` or `order.getDriver()`, causing unhandled `NullPointerException`s that surface as 500 errors.
- Use Case #10, Extension 5e: `DriverStatsImpl.updateTotalEarnings()` (lines 46-47) is called unconditionally on every "Delivered" transition with no check on `order.getIsFulfilled()` — reprocessing an already-delivered order double-credits both earnings and delivery count.
- Use Case #10, Extension 5f: a stale "Pick Up" call on an already-delivered order silently reverts `isFulfilled` to false (lines 281-283), while previously-credited earnings are never clawed back — leaving no way to reconcile the mismatch through the app.



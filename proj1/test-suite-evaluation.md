## Finding 7: Use Case #7 (Delete user account) has essentially zero coverage of its own extensions

`UserControllerTest.shouldDeleteUserWhenAdmin` is the only pre-existing test that
exercises `DELETE /api/users/{id}`:

```java
@Test
@WithMockUser(roles = "ADMIN")
void shouldDeleteUserWhenAdmin() throws Exception {
    mockMvc.perform(delete("/api/users/" + testUser.getId()))
            .andExpect(status().isOk());
    mockMvc.perform(get("/api/users/" + testUser.getId()))
            .andExpect(status().isNotFound());
}
```

It deletes a user that is not the caller, has no orders, is not a driver, and is
not the last admin, the one case in which nothing can go wrong. Every extension
the use case itself documents is untouched:

| Extension | What it claims | Pre-existing test | Verdict |
| --- | --- | --- | --- |
| 2a: self-delete | Admin can delete their own account; no backend guard | none | uncovered |
| 2b: delete a non-existent user | Returns 200 instead of 404 | none | uncovered |
| 5a: user has placed orders | Orders are hard-deleted with no warning | none | uncovered |
| 5b: deleted user is a driver | `DriverStats` row is permanently orphaned | none | uncovered |
| 5c: last remaining admin | No guard; platform left with zero admins | none | uncovered |

Five documented failure extensions, five with no test. Our own
`shouldNotActuallyDeleteAdminAccount_onSelfDeleteAttempt` (extension 2a) is a red
test for exactly this reason: nothing in the pre-existing suite would have told
anyone the guard was frontend-only.

*Also corroborates Finding 1 above*: all ten of `FoodControllerTest.java`'s
pre-existing tests, `testGetFoods`, `testCreateFood`, `testUpdateFood`,
`testCreateFoodDuplicateName`, `testCreateFoodInvalid`, `testDeleteFoodSuccess`,
`testDeleteFoodNotFound`, `testUpdateFoodMissingName`, `testUpdateFoodNotFound`,
`testUpdateFoodInvalidValues`, are annotated
`@WithMockUser(username = "staff", roles = "STAFF")` with no exception. A
`CUSTOMER` or unauthenticated caller is never tried once. Two new red tests,
written against Use Case #8 extension 2a and Use Case #9 extension 1a, confirm
the consequence directly: a `CUSTOMER` account can call both `POST /api/foods`
and `DELETE /api/foods/{id}` and succeed.

## Finding 8: two pre-existing driver tests send a status value that doesn't match the code, and pass without testing anything

`OrderControllerTest.java` has two tests, both added under the comment
`// --- Missing tests added below ---`, that are meant to exercise a driver picking
up an order:

```java
void testGetActiveOrders_ForDriver() throws Exception {
    ...
    orderService.updateOrder(saved.getId(), "driver", "PICKED_UP");
    mvc.perform(get("/api/orders/activeOrders/driver"))
            .andExpect(status().isOk());
}

void testUpdateOrderStatus_AsDriver() throws Exception {
    ...
    String payload = "{\"username\":\"driver\",\"status\":\"PICKED_UP\"}";
    mvc.perform(post("/api/orders/" + saved.getId())
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(payload))
            .andExpect(status().isOk());
}
```

Both send the literal string `"PICKED_UP"`. `OrderServiceImpl.updateOrder()`
requires an exact match against `"Picked Up"` (line 274,
`status.equals("Picked Up")`) before it will assign a driver to the order.
`"PICKED_UP".equals("Picked Up")` is false, so the driver-assignment branch never
runs, so the order's `driver` field stays null, and its `status` column is left
holding the literal, non-canonical string `"PICKED_UP"`.

The consequence compounds in `testGetActiveOrders_ForDriver`:
`OrderServiceImpl.getActiveOrders()` queries
`orderRepository.findByDriverUsernameAndStatus(username, "Picked Up")`, the same
exact-match string, and now also a driver field that was never set. The query can
only return an empty list. The test asserts `status().isOk()` and nothing else;
it never checks that the returned list contains the order, or that it is
non-empty. Both tests pass every time, and both pass without ever exercising the
driver-assignment code path their names claim to test.

This is a defect in the *tests*, not in the application, but it means Use Case
#10's main success scenario (driver picks up, then delivers an order) had a
green-looking but empty test before our own coverage was added.

*Also relevant to Finding 5 above* (vacuous tests): this is the same class of
problem (a test that reports green without exercising the behavior its name
claims), found independently in `OrderControllerTest.java` rather than
`DriverDashboardTest`/`frontend`.

## Addendum to "What this implies for our own tests"

A separate JUnit suite (29 tests, Use Cases #6-#10) reaches the same conclusion
as the pytest suite above, from a different angle. It found 17 real defects the
same way: expected values were taken from the use cases' own extensions, not
from the code. Four of those tests were written twice on purpose: once
asserting the code's actual (buggy) behavior, once asserting the behavior the
use case actually specifies, and the second version fails every time, which is
the point: a failing test against a real fault is a finding, not a mistake.

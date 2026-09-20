# Driver-statistics access tests

Run these focused tests before moving on to the next Foodseer fix.

## Requirements and commands

Use JDK 21 and Maven. These tests do not need MySQL, Docker, application.properties,
or a running backend/frontend. Maven needs internet access on the first run if
dependencies are not already cached.

From `food-seer-backend`, run:

```sh
mvn -Dtest=DriverStatsSecurityTest,DriverStatsControllerTest,DriverStatsImplTest test
```

On this Mac, Maven defaults to Java 26 even though `java -version` reports 21.
Select the installed Java 21 explicitly:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
  mvn -Dtest=DriverStatsSecurityTest,DriverStatsControllerTest,DriverStatsImplTest test
```

To run only the new security cases, use `-Dtest=DriverStatsSecurityTest`.
Results and JUnit XML are written to `target/surefire-reports/`. Maven returns
a nonzero exit status if tests fail. Restricted agent sandboxes may prevent
Mockito from attaching its Java test agent; run from a normal terminal in that case.

## What is covered

`src/test/java/FoodSeer/controller/DriverStatsSecurityTest.java` contains 14 cases:

- Anonymous requests receive 401, whether or not the requested driver exists.
- Customers, staff, and other drivers receive 403.
- Ownership alone does not give customers or staff driver privileges.
- Drivers can access their own statistics after username or email authentication.
- Administrators can access another driver's statistics.
- Two drivers have distinct, nonzero statistics; successful responses are checked
  against the requested driver's values.
- An administrator receives 404 for missing statistics; an unrelated driver
  receives 403 before the statistics service is called.

The test loads the production security configuration, method authorization,
password authentication, user-details service, JWT signing, and JWT filter.
Only the user repository and statistics service are mocked. Tokens are generated
after password authentication through `AuthenticationManager`; the HTTP login
endpoint, database persistence, and browser UI are not covered by this test.

The existing `DriverStatsControllerTest` and `DriverStatsImplTest` add six cases
for controller response behavior and service logic. The controller slice still
disables filters intentionally; the new security test supplies authorization coverage.

## Optional live API regression

The existing `../proj1/tests/test_driver_stats_access_pytest.py` has also been
updated so an anonymous request for a nonexistent username expects 401.
It creates accounts and requires an explicitly selected disposable test backend.
From the repository root, with pytest installed and that backend running:

```sh
API_BASE_URL=http://localhost:8080 \
  python3 -m pytest -v proj1/tests/test_driver_stats_access_pytest.py
```

This live API suite is separate from the focused Java checks. The general
`run_all_tests.sh` runner still always exits zero and has not been repaired in
this change. A focused pass does not establish that the full regression suite passes.

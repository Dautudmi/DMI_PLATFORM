# Architecture Principles

1. Core never depends on Apps.

2. Apps communicate with Core only through public APIs.

3. One Stage = One Responsibility.

4. Pipeline orchestrates only.

5. Services coordinate, not calculate.

6. Providers load data only.

7. Factories build domain objects only.

8. Domain Models are the Source of Truth.

9. Derived values belong in Analysis or Reports.

10. Dependency Injection is mandatory.

11. Every new module requires unit tests.

12. Architecture changes require an RFC.

13. Prefer composition over inheritance.

14. Public APIs should remain stable whenever possible.

15. Readability is preferred over cleverness.
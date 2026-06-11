# Testing

> [!TIP]
> Return back to the [README.md](README.md) file.

This document outlines the testing strategy and evidence for **PropHouse**, a Django-based full stack web application built as part of the Code Institute Milestone 4 (Full Stack Development) project.

Testing has been carried out throughout development using a combination of **automated tests**, **manual user acceptance testing**, and **external validation tools**, in line with the assessment requirements.

## Automated Testing

### Test Driven Development

TDD was used throughout development to investigate bugs, validate business rules and safely refactor application behaviour.

Unit tests were written to thoroughly automate testing of model, view and service behaviour.

### Service Layer Testing

#### Service Layer Business Rules

| Service                      | Business Rule                                   | Tested |
| ---------------------------- | ----------------------------------------------- | ------ |
| BasketService                | Basket remains associated with user session     | Pass   |
| AddressService               | Invalid addresses are rejected                  | Pass   |
| AddressService               | Only one default address may exist per user     | Pass   |
| MembershipService            | Discounts applied to active members             | Pass   |
| CheckoutService              | Store delivery address snapshot                 | Pass   |
| CheckoutService              | Empty baskets cannot enter checkout             | Pass   |
| Warehouse Fulfilment Service | Stock updated only after payment                | Pass   |
| Warehouse Fulfilment Service | Insufficient stock results in failed fulfilment | Pass   |

Service-layer tests were used to verify business rules independently from views and templates. This approach allowed complex checkout, basket, membership and fulfilment behaviour to be tested in isolation without requiring full HTTP request cycles.

```bash
[12/06/26 12:17:48] .venv ❯ python manage.py test
Found 10 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 10 tests in 1.073s

OK
Destroying test database for alias 'default'...
```

### Basket Session Persistence

During automated testing, a basket session persistence test revealed
that guest baskets could be created before a session key existed,
preventing reliable basket recovery. The issue was resolved by
ensuring a session was created before basket lookup and creation.

### Address Service

Address service tests were written during implementation of the saved-address feature.

These tests validate:

- Valid address data passes form validation.
- Invalid address data returns validation errors.
- Default addresses can be saved successfully.
- Existing default addresses are replaced correctly.

During development, the tests exposed a runtime issue where the `Address` model was not imported correctly within the service layer. The failing test identified the defect immediately and the implementation was corrected before integration into the checkout workflow.

Example test execution:

```bash
python manage.py test accounts.tests.test_address_service
```

Result:

```text
Found 3 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...
----------------------------------------------------------------------
Ran 3 tests in 0.341s

OK
Destroying test database for alias 'default'...
```

_These tests provide confidence that address validation and persistence
behave correctly before integration into the wider checkout workflow._

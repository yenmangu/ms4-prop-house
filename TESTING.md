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

| Service                       | Business Rule                                    | Tested |
| ----------------------------- | ------------------------------------------------ | ------ |
| BasketService                 | Basket remains associated with user session      | Pass   |
| AddressService                | Invalid addresses are rejected                   | Pass   |
| AddressService                | Only one default address may exist per user      |        |
| MembershipService             | Discounts applied to active members              | Pass   |
| CheckoutService               | Store delivery address snapshot                  | Pass   |
| CheckoutService               | Empty baskets cannot enter checkout              | Pass   |
| Warehouse FulFillment Service | Stock updated only after payment                 |        |
| Warehouse FulFillment Service | Insufficient stock results in failed fulfillment |        |

Service-layer tests were used to verify business rules independently from views and templates.

### Basket Session Persistence

During development, a defect was identified where basket operations appeared to lose the user's basket between requests.

A dedicated test was written to verify that:

- A basket is created correctly when an item is added.
- The `basket_id` is stored in the user's session.
- The session persists between requests.
- Removing an item does not create a new session.

This test was used to diagnose and resolve session-management issues within the basket workflow.

_These tests ensure that a customer's basket remains associated with
their session throughout the shopping and checkout process._

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
Found 2 test(s).
System check identified no issues (0 silenced).
..
----------------------------------------------------------------------
Ran 2 tests in 0.225s

OK
```

_These tests provide confidence that address validation and persistence
behave correctly before integration into the wider checkout workflow._

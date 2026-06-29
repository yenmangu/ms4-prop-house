# Testing

> [!TIP]
> Return back to the [README.md](README.md) file.

This document outlines the testing strategy and evidence for **PropHouse**, a Django-based full stack web application built as part of the Code Institute Milestone 4 (Full Stack Development) project.

Testing has been carried out throughout development using a combination of **automated tests**, **manual user acceptance testing**, and **external validation tools**, in line with the assessment requirements.

## Code Validation

### CSS

All custom CSS files were validated using the **W3C Jigsaw CSS Validator**.

| File          | Purpose                 | Result | Screenshot                                                               |
| ------------- | ----------------------- | ------ | ------------------------------------------------------------------------ |
| accounts.css  | Accounts app styles     | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/accounts.png)  |
| admin.css     | Admin app styles        | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/admin.png)     |
| auth.css      | Auth app styles         | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/auth.png)      |
| basket.css    | Basket app styles       | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/basket.png)    |
| catalogue.css | Catalogue app styles    | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/catalogue.png) |
| core.css      | Core app styles         | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/core.png)      |
| dashboard.css | Dashboard app styles    | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/dashboard.png) |
| detail.css    | Catalogue-Detail styles | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/detail.png)    |
| theme.css     | Themes and root vars    | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/theme.png)     |
| toast.css     | Toast styles            | Pass   | ![CSS Valdiation](./documentation/evidence/css_validation/toast.png)     |

There are no errors present in my own custom CSS implementations.

### Python

Python code quality was assessed through:

- Django’s built-in system checks
- Manual review against **PEP8** standards
- Automated Django test execution

All custom Python files follow consistent naming, indentation, and descriptive variable conventions.

---

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

---

## Defensive Programming

Manual testing was carried out to ensure the application behaves safely and predictably under invalid or unexpected user actions.
All defensive behaviours are enforced server-side and verified via manual interaction.

| Feature                                  | Expectation                                               | Result | Notes                                       | Evidence                                                   |
| ---------------------------------------- | --------------------------------------------------------- | ------ | ------------------------------------------- | ---------------------------------------------------------- |
| Unauthorised edit (Not logged in)        | Anonymous users blocked                                   | Pass   | Toast shows login required                  | ![Evidence](./documentation/defensive/login-required.png)  |
| Real time auth validation                | Validation errors shown                                   | Pass   | Browser independant validation confirmed    | ![Evidence](./documentation/defensive/auth-validation.png) |
| Auth gated navbar items                  | My bookings not available to anonymous users              | Pass   | Navbar renders content gated by auth status | ![Evidence](./documentation/defensive/dynamic-navbar.png)  |
| Ensure empty results do not break search | User message displayed when search returns empty          | Pass   | User message confirmed in industrial style  | ![Evidence](./documentation/defensive/nothing-found.png)   |
| Live stock status ensures no empty hires | Check availability not available when stock level is zero | Pass   | Confirmed                                   | ![Evidence](./documentation/defensive/stock-status.png)    |

## Responsiveness

The application was tested across multiple viewport sizes using browser developer tools and real devices.

| Page                          | Mobile | Tablet | Desktop | Notes                                       |
| ----------------------------- | ------ | ------ | ------- | ------------------------------------------- |
| Home / Catalogue              | Pass   | Pass   | Pass    | Grid adapts cleanly                         |
| Product Detail                | Pass   | Pass   | Pass    | Content stacks correctly                    |
| Checkout / Availability Forms | Pass   | Pass   | Pass    | Inputs remain usable                        |
| Membership                    | Pass   | Pass   | Pass    | Cards stack correctly                       |
| Dashboard                     | Pass   | Pass   | Pass    | Table resizes correctly                     |
| Authentication                | Pass   | Pass   | Pass    | No overflow, inputs remain usable and clear |

### Responsiveness Evidence

| Page             | Mobile                                                                   | Tablet                                                                   | Desktop                                                                   |
| ---------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Home / Catalogue | ![Mobile Screenshot](documentation/responsiveness/mobile/home.png)       | ![Tablet Screenshot](documentation/responsiveness/tablet/home.png)       | ![Desktop Screnshot](documentation/responsiveness/desktop/home.png)       |
| Product Detail   | ![Mobile Screenshot](documentation/responsiveness/mobile/detail.png)     | ![Tablet Screenshot](documentation/responsiveness/tablet/detail.png)     | ![Desktop Screnshot](documentation/responsiveness/desktop/detail.png)     |
| Basket           | ![Mobile Screenshot](documentation/responsiveness/mobile/basket.png)     | ![Tablet Screenshot](documentation/responsiveness/tablet/basket.png)     | ![Desktop Screnshot](documentation/responsiveness/desktop/basket.png)     |
| Checkout         | ![Mobile Screenshot](documentation/responsiveness/mobile/checkout.png)   | ![Tablet Screenshot](documentation/responsiveness/tablet/checkout.png)   | ![Desktop Screnshot](documentation/responsiveness/desktop/checkout.png)   |
| Dashbaord        | ![Mobile Screenshot](documentation/responsiveness/mobile/dashboard.png)  | ![Tablet Screenshot](documentation/responsiveness/tablet/dashboard.png)  | ![Desktop Screnshot](documentation/responsiveness/desktop/dashboard.png)  |
| Membership       | ![Mobile Screenshot](documentation/responsiveness/mobile/membership.png) | ![Tablet Screenshot](documentation/responsiveness/tablet/membership.png) | ![Desktop Screnshot](documentation/responsiveness/desktop/membership.png) |

### Browser Compatibility Breakdown

Each core feature was manually tested across multiple browsers and devices to ensure consistent behaviour and layout.

| Feature                       | Chrome                                                                | Opera                                                               | Safari                                                                | iOS (Safari)                                         |
| ----------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------- |
| Catalogue                     | ![Chrome Report](documentation/browser/chrome/home.png)               | ![Opera Report](documentation/browser/opera/home.png)               | ![Safari Report](documentation/browser/safari/home.png)               | ![iOS Report](documentation/browser/chrome/home.png) |
| Catalogue - Search            | ![Chrome Report](documentation/browser/chrome/search.png)             | ![Opera Report](documentation/browser/opera/search.png)             | ![Safari Report](documentation/browser/safari/search.png)             | ![iOS Report](documentation/browser/chrome/home.png) |
| Product Detail                | ![Chrome Report](documentation/browser/chrome/detail.png)             | ![Opera Report](documentation/browser/opera/detail.png)             | ![Safari Report](documentation/browser/safari/detail.png)             | ![iOS Report](documentation/browser/chrome/home.png) |
| Product Detail - Availability | ![Chrome Report](documentation/browser/chrome/check-availability.png) | ![Opera Report](documentation/browser/opera/check-availability.png) | ![Safari Report](documentation/browser/safari/check-availability.png) | ![iOS Report](documentation/browser/chrome/home.png) |
| Basket-add                    | ![Chrome Report](documentation/browser/chrome/add-basket.png)         | ![Opera Report](documentation/browser/opera/add-basket.png)         | ![Safari Report](documentation/browser/safari/add-basket.png)         | ![iOS Report](documentation/browser/chrome/home.png) |
| Basket                        | ![Chrome Report](documentation/browser/chrome/basket.png)             | ![Opera Report](documentation/browser/opera/basket.png)             | ![Safari Report](documentation/browser/safari/basket.png)             | ![iOS Report](documentation/browser/chrome/home.png) |
| Checkout flow - contact info  | ![Chrome Report](documentation/browser/chrome/checkout-contact.png)   | ![Opera Report](documentation/browser/opera/checkout-contact.png)   | ![Safari Report](documentation/browser/safari/checkout-contact.png)   | ![iOS Report](documentation/browser/chrome/home.png) |
| Checkout flow - Stripe        | ![Chrome Report](documentation/browser/chrome/checkout-stripe.png)    | ![Opera Report](documentation/browser/opera/checkout-stripe.png)    | ![Safari Report](documentation/browser/safari/checkout-stripe.png)    | ![iOS Report](documentation/browser/chrome/home.png) |
| Checkout Complete             | ![Chrome Report](documentation/browser/chrome/checkout-success.png)   | ![Opera Report](documentation/browser/opera/checkout-success.png)   | ![Safari Report](documentation/browser/safari/checkout-success.png)   | ![iOS Report](documentation/browser/chrome/home.png) |
| Dashboard                     | ![Chrome Report](documentation/browser/chrome/dashboard.png)          | ![Opera Report](documentation/browser/opera/dashboard.png)          | ![Safari Report](documentation/browser/safari/dashboard.png)          | ![iOS Report](documentation/browser/chrome/home.png) |
| Dashboard - Search            | ![Chrome Report](documentation/browser/chrome/dashboard-search.png)   | ![Opera Report](documentation/browser/opera/dashboard-search.png)   | ![Safari Report](documentation/browser/safari/dashboard-search.png)   | ![iOS Report](documentation/browser/chrome/home.png) |
| PDF                           | ![Chrome Report](documentation/browser/chrome/pdf.png)                | ![Opera Report](documentation/browser/opera/pdf.png)                | ![Safari Report](documentation/browser/safari/pdf.png)                | ![iOS Report](documentation/browser/chrome/home.png) |

---

## Lighthouse Audit

Lighthouse audits were conducted using Chrome DevTools on key user-facing pages to assess performance, accessibility, best practices, and SEO. Tests were run in both **mobile** and **desktop** modes using Lighthouse’s default throttling profiles.

Screenshots of the audit results are stored in `documentation/lighthouse/reports/`.

### Lighthouse Results Table

| Page / View    | Mobile Result                                                   | Desktop Result                                                    |
| -------------- | --------------------------------------------------------------- | ----------------------------------------------------------------- |
| Home/Catalogue | [Mobile Report](documentation/lighthouse/mobile/home.png)       | [Desktop Report](documentation/lighthouse/desktop/home.png)       |
| Product Detail | [Mobile Report](documentation/lighthouse/mobile/detail.png)     | [Desktop Report](documentation/lighthouse/desktop/detail.png)     |
| Basket         | [Mobile Report](documentation/lighthouse/mobile/basket.png)     | [Desktop Report](documentation/lighthouse/desktop/home.png)       |
| Membership     | [Mobile Report](documentation/lighthouse/mobile/membership.png) | [Desktop Report](documentation/lighthouse/desktop/membership.png) |
| Dashboard      | [Mobile Report](documentation/lighthouse/mobile/dashboard.png)  | [Desktop Report](documentation/lighthouse/desktop/dashboard.png)  |

> [!NOTE]
> Its important to note that the lower score on mobile is due to loading the Stripe.JS script.
> This is completely unnavoidable and efforts have been taken to ensure this script is loaded _only_ on the necessaery pages.

---

## Bugs found during testing

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

### Large Image Serving

During validation and Lighthouse testing, it became apparent that larger images than were required were being served from Cloudinary.
![Oversized Image Delivery](documentation/evidence/oversized_image_delivery.png)

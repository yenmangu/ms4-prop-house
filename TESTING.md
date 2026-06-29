# Testing

> [!TIP]
> Return back to the [README.md](README.md) file.

This document outlines the testing strategy and evidence for **PropHouse**, a Django-based full stack web application built as part of the Code Institute Milestone 4 (Full Stack Development) project.

Testing has been carried out throughout development using a combination of **automated tests**, **manual user acceptance testing**, and **external validation tools**, in line with the assessment requirements.

## Code Validation

### HTML

> [!NOTE]
> HTML validation was carried out using a [**custom Python CLI tool**](https://github.com/yenmangu/w3c-command-line-validator) that consumes the **W3C Nu HTML Checker HTTP API**.
>
> Validation was performed **against deployed URLs**, ensuring that the results reflect the fully rendered production state of the application rather than local templates.
>
> The tool was run against all major routes in the application, including authenticated pages and querystring-based routes, with one exception: `/accounts/dashboard` cannot be automatically validated as it requires authorisation. A separate evidence for this is linked in the table.
>
> **Full validation output is provided as evidence** in the following report:
>
> [Validation Report](documentation/validation/w3c_validation_report_2026-06-29.txt)

| Page / Template  | URL (Deployed)                                                     | Errors | Evidence                                                                        |
| ---------------- | ------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------- |
| Home / Catalogue | https://prop-house-f6d4754d8ee5.herokuapp.com/                     | 0\*    | See full report                                                                 |
| Basket           | https://prop-house-f6d4754d8ee5.herokuapp.com/basket/              | 0\*    | See full report                                                                 |
| Membership       | https://prop-house-f6d4754d8ee5.herokuapp.com/accounts/membership/ | 0\*    | See full report                                                                 |
| Dashboard        | https://prop-house-f6d4754d8ee5.herokuapp.com/accounts/dashboard/  | 0\*    | [dashboard_validation.pdf](./documentation/validation/dashboard_validation.pdf) |
| Signup           | https://prop-house-f6d4754d8ee5.herokuapp.com/accounts/signup/     | 0\*    | See full report                                                                 |

\*All reported errors are HTMX attributes — see note below.

> [!NOTE]
> HTMX attributes such as `hx-get`, `hx-post`, `hx-target`, and `hx-swap` will
> appear as W3C validation errors since they are non-standard HTML attributes.
> This is expected — HTMX is valid in practice but not in the HTML5 spec. To
> suppress these errors, HTMX supports `data-*` equivalents (`data-hx-get` etc.)
> which are spec-compliant, though most projects simply accept the warnings.

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

![Black validation](./documentation/validation/black-valdiation.png)

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
| Dashboard        | ![Mobile Screenshot](documentation/responsiveness/mobile/dashboard.png)  | ![Tablet Screenshot](documentation/responsiveness/tablet/dashboard.png)  | ![Desktop Screnshot](documentation/responsiveness/desktop/dashboard.png)  |
| Membership       | ![Mobile Screenshot](documentation/responsiveness/mobile/membership.png) | ![Tablet Screenshot](documentation/responsiveness/tablet/membership.png) | ![Desktop Screnshot](documentation/responsiveness/desktop/membership.png) |

### Browser Compatibility Breakdown

Each core feature was manually tested across multiple browsers and devices to ensure consistent behaviour and layout.

| Feature                       | Chrome                                                                | Opera                                                               | Safari                                                                | iOS (Safari)                                                    |
| ----------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------- |
| Catalogue                     | ![Chrome Report](documentation/browser/chrome/home.png)               | ![Opera Report](documentation/browser/opera/home.png)               | ![Safari Report](documentation/browser/safari/home.png)               | ![iOS Report](documentation/browser/iOS/home.png)               |
| Catalogue - Search            | ![Chrome Report](documentation/browser/chrome/search.png)             | ![Opera Report](documentation/browser/opera/search.png)             | ![Safari Report](documentation/browser/safari/search.png)             | ![iOS Report](documentation/browser/iOS/search.png)             |
| Product Detail                | ![Chrome Report](documentation/browser/chrome/detail.png)             | ![Opera Report](documentation/browser/opera/detail.png)             | ![Safari Report](documentation/browser/safari/detail.png)             | ![iOS Report](documentation/browser/iOS/detail.png)             |
| Product Detail - Availability | ![Chrome Report](documentation/browser/chrome/check-availability.png) | ![Opera Report](documentation/browser/opera/check-availability.png) | ![Safari Report](documentation/browser/safari/check-availability.png) | ![iOS Report](documentation/browser/iOS/check-availability.png) |
| Basket-add                    | ![Chrome Report](documentation/browser/chrome/add-basket.png)         | ![Opera Report](documentation/browser/opera/add-basket.png)         | ![Safari Report](documentation/browser/safari/add-basket.png)         | ![iOS Report](documentation/browser/iOS/add-basket.png)         |
| Basket                        | ![Chrome Report](documentation/browser/chrome/basket.png)             | ![Opera Report](documentation/browser/opera/basket.png)             | ![Safari Report](documentation/browser/safari/basket.png)             | ![iOS Report](documentation/browser/iOS/basket.png)             |
| Checkout flow - contact info  | ![Chrome Report](documentation/browser/chrome/checkout-contact.png)   | ![Opera Report](documentation/browser/opera/checkout-contact.png)   | ![Safari Report](documentation/browser/safari/checkout-contact.png)   | ![iOS Report](documentation/browser/iOS/checkout-contact.png)   |
| Checkout flow - Stripe        | ![Chrome Report](documentation/browser/chrome/checkout-stripe.png)    | ![Opera Report](documentation/browser/opera/checkout-stripe.png)    | ![Safari Report](documentation/browser/safari/checkout-stripe.png)    | ![iOS Report](documentation/browser/iOS/checkout-stripe.png)    |
| Checkout Complete             | ![Chrome Report](documentation/browser/chrome/checkout-success.png)   | ![Opera Report](documentation/browser/opera/checkout-success.png)   | ![Safari Report](documentation/browser/safari/checkout-success.png)   | ![iOS Report](documentation/browser/iOS/checkout-success.png)   |
| Dashboard                     | ![Chrome Report](documentation/browser/chrome/dashboard.png)          | ![Opera Report](documentation/browser/opera/dashboard.png)          | ![Safari Report](documentation/browser/safari/dashboard.png)          | ![iOS Report](documentation/browser/iOS/dashboard.png)          |
| Dashboard - Search            | ![Chrome Report](documentation/browser/chrome/dashboard-search.png)   | ![Opera Report](documentation/browser/opera/dashboard-search.png)   | ![Safari Report](documentation/browser/safari/dashboard-search.png)   | ![iOS Report](documentation/browser/iOS/dashboard-search.png)   |
| PDF                           | ![Chrome Report](documentation/browser/chrome/pdf.png)                | ![Opera Report](documentation/browser/opera/pdf.png)                | ![Safari Report](documentation/browser/safari/pdf.png)                | ![iOS Report](documentation/browser/iOS/pdf.png)                |

---

## Lighthouse Audit

Lighthouse audits were conducted using Chrome DevTools on key user-facing pages to assess performance, accessibility, best practices, and SEO. Tests were run in both **mobile** and **desktop** modes using Lighthouse’s default throttling profiles.

Screenshots of the audit results are stored in `documentation/lighthouse/reports/`.

### Lighthouse Results Table

| Page / View    | Mobile Result                                                   | Desktop Result                                                    |
| -------------- | --------------------------------------------------------------- | ----------------------------------------------------------------- |
| Home/Catalogue | [Mobile Report](documentation/lighthouse/mobile/home.png)       | [Desktop Report](documentation/lighthouse/desktop/home.png)       |
| Product Detail | [Mobile Report](documentation/lighthouse/mobile/detail.png)     | [Desktop Report](documentation/lighthouse/desktop/detail.png)     |
| Basket         | [Mobile Report](documentation/lighthouse/mobile/basket.png)     | [Desktop Report](documentation/lighthouse/desktop/basket.png)     |
| Membership     | [Mobile Report](documentation/lighthouse/mobile/membership.png) | [Desktop Report](documentation/lighthouse/desktop/membership.png) |
| Dashboard      | [Mobile Report](documentation/lighthouse/mobile/dashboard.png)  | [Desktop Report](documentation/lighthouse/desktop/dashboard.png)  |

> [!NOTE]
> It's important to note that the lower score on mobile is due to loading the Stripe.JS script.
> This is completely unavoidable and efforts have been taken to ensure this script is loaded _only_ on the necessary pages.

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

During Lighthouse testing, it became apparent that Cloudinary was serving images at a larger resolution than required for the viewport being rendered, resulting in unnecessary page weight on mobile devices.

![Oversized Image Delivery](documentation/evidence/oversized_image_delivery.png)

The fix was implemented in `catalogue/templates/_detail_image.html` by adding a `srcset` attribute with an additional `420w` breakpoint and a corresponding `sizes` rule of `(max-width: 480px) 100vw`. This instructs the browser to request the appropriately-sized image variant from Cloudinary based on the actual viewport width, rather than always fetching the full-size asset.

This reduced mobile image payload by approximately 24KB and contributed to the improved Lighthouse performance score on mobile.

---

> [!TIP]
> Full incident reports for all bugs above, including root cause analysis and commit references, are documented in [BUG_REPORT.md](documentation/bugs/BUG_REPORT.md).

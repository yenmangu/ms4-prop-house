## Live Application

- **Live site:** [Prop House](https://prop-house-f6d4754d8ee5.herokuapp.com)
- **Repository:** [yenmangu/ms4-prop-house](https://github.com/yenmangu/ms4-prop-house)

---

# Overview

PropHouse is a digital hire platform designed for production companies and creative teams to browse, hire, and manage prop and equipment orders online.

All products are available for direct hire through a standard e-commerce checkout flow. In addition, users may subscribe to an optional membership plan which provides discounted pricing on eligible products. Membership enhances value through pricing benefits rather than gated access.

The core journey of the application is:

**Browse → Add to Basket → Checkout → Hire**

The platform is built using Django with a relational database and Stripe (test mode) for payment processing. It follows an accessibility-first, mobile-first approach aligned to WCAG 2.1 AA and the Code Institute Level 5 specification.

---

# Glossary

| Term         | Definition                                                                              |
| ------------ | --------------------------------------------------------------------------------------- |
| Product      | A hireable prop or equipment item available on the platform.                            |
| Category     | A grouping used to organise products by type or purpose.                                |
| Basket       | A temporary collection of products selected for hire prior to checkout.                 |
| Order        | A completed hire transaction created after successful payment.                          |
| Membership   | An optional subscription that provides percentage-based discounts on eligible products. |
| Subscription | A recurring Stripe-managed payment granting membership benefits.                        |
| MoSCoW       | A prioritisation method: Must, Should, Could, Won’t Have.                               |

---

# UX

## The 5 Planes of UX

### 1. Strategy Plane

**Purpose**
PropHouse exists to provide a streamlined digital experience for hiring props and equipment. It removes friction from traditional email-based or phone-based booking workflows by offering clear pricing, structured browsing, and secure online checkout.

**Business / User Goals**

- Enable production teams to quickly source and hire required items.
- Provide transparent pricing and availability.
- Offer membership incentives for repeat clients.
- Reduce administrative overhead through automated order management.

**Primary User Needs**

- Browse products clearly by category.
- View detailed product information before hiring.
- Understand pricing and discounts.
- Complete secure online payments.
- Access order history and saved addresses.

---

### 2. Scope Plane

**Core Features (Delivered)**

- Product browsing and categorisation.
- Product detail pages.
- Basket functionality.
- Secure Stripe checkout (test mode).
- User registration and authentication.
- Order history dashboard.
- Saved address management.
- Membership subscription with discount logic.

**Future Features (Could-Have)**

- Availability calendar.
- Wishlist functionality.
- Product reviews.
- Automated return tracking.
- Advanced filtering and search.

**Out of Scope (Explicitly Not Implemented)**

- Live booking conflict detection.
- Logistics and delivery scheduling.
- Damage deposit workflows.
- Warehouse location tracking.
- Reservation system separate from paid checkout.

---

### 3. Structure Plane

**Information Architecture**

- Home → Product Catalogue
- Product Catalogue → Product Detail
- Product Detail → Add to Basket
- Basket → Checkout
- Checkout → Order Confirmation
- Account Dashboard → Orders / Addresses / Membership

**Primary User Flow**

1. User lands on home page.
2. Browses or filters products.
3. Views product detail.
4. Adds item(s) to basket.
5. Registers or logs in (if required).
6. Completes Stripe checkout.
7. Receives confirmation and can view order in dashboard.

---

### 4. Skeleton Plane

Wireframes were created to plan layout and interaction patterns before development, focusing on:

- Clear product imagery hierarchy.
- Transparent pricing display.
- Distinct basket summary section.
- Clear separation between membership pricing and standard pricing.
- Minimal friction checkout process.

| Page           | Wireframe    |
| -------------- | ------------ |
| Home           | (Figma link) |
| Product List   | (Figma link) |
| Product Detail | (Figma link) |
| Basket         | (Figma link) |
| Checkout       | (Figma link) |

---

### 5. Surface Plane

#### Colour Scheme

| Purpose | Colour | Usage                         |
| ------- | ------ | ----------------------------- |
| Primary |        | Headings, navigation          |
| Accent  |        | Primary actions, buttons      |
| Success |        | Order confirmation messages   |
| Warning |        | Important notices             |
| Error   |        | Validation and payment errors |

#### Typography

System font stack used for performance and clarity.
Semantic heading structure (`h1` → `h2` → `h3`) enforced.

#### Imagery

- High-quality product images used where available.
- Placeholder handling implemented to prevent layout shift.
- Images include meaningful `alt` text.

#### Interactivity & Feedback

- Basket updates reflect immediately in the UI.
- Pricing recalculates dynamically (including membership discounts where applicable).
- Stripe checkout provides clear success/failure feedback.
- All feedback messages are ARIA-announced.

#### Summary

The interface prioritises clarity, professional presentation, and usability. Visual styling supports trust and transparency in the hiring process.

---

# Project Planning & Agile Methodology

## MoSCoW Prioritisation

- **Must Have:** Product catalogue, basket, checkout, Stripe integration, authentication, order management.
- **Should Have:** Membership discounts, address book.
- **Could Have:** Wishlist, advanced filtering.
- **Won’t Have:** Full logistics management system.

---

## User Stories

| ID  | User Story              | MoSCoW Priority | File |
| --- | ----------------------- | --------------- | ---- |
| 01  | Browse products         | Must            |      |
| 02  | View product detail     | Must            |      |
| 03  | Add to basket           | Must            |      |
| 04  | Checkout with Stripe    | Must            |      |
| 05  | Register / Login        | Must            |      |
| 06  | Manage saved addresses  | Should          |      |
| 07  | Subscribe to membership | Should          |      |

---

# Features

## Existing Features

| Feature                 | User Story ID | MoSCoW Priority | Implemented |
| ----------------------- | ------------- | --------------- | ----------- |
| Product Catalogue       | 01            | Must            | Y           |
| Product Detail          | 02            | Must            | Y           |
| Basket                  | 03            | Must            | Y           |
| Stripe Checkout         | 04            | Must            | Y           |
| Authentication          | 05            | Must            | Y           |
| Address Management      | 06            | Should          | Y           |
| Membership Subscription | 07            | Should          | Y           |

---

# Database Design

PropHouse uses a relational database to manage catalogue items, customer accounts, memberships, baskets, orders, fulfilment records, and saved delivery addresses.

The schema evolved throughout development as requirements around membership pricing, checkout, fulfilment, and inventory management became clearer.

> [!NOTE]
> For the complete database design documentation, model breakdowns, relationship diagrams, and app ownership structure, see:
>
> [Database Design Documentation](documentation/database/database-design.md)

## Entity Relationship Diagram

![PropHouse ERD](documentation/database/prop-house-erd.png)

---

# Architecture

## High-Level Overview

- Django templates for server-side rendering.
- Django ORM for relational data modelling.
- Stripe test API for payments and subscriptions.
- Modular apps aligned to domain boundaries.

## Request Pipeline & State Management

The application utilizes a **Single Source of Truth** architecture to manage the basket state across the entire request lifecycle. This ensures that the UI (navigation badges, totals) and the business logic (adding/removing items) are always synchronized.

### 1. The Service Layer (`basket/services.py`)

To prevent logic fragmentation, all basket retrieval and recovery logic is centralized in a dedicated service layer. This layer handles the hierarchical lookup of a basket:

- **Authenticated User**: Priority check for an existing `OPEN` basket linked to the user account.
- **Session ID**: Secondary check for a specific `basket_id` stored in the browser session.
- **Orphan Recovery**: A fallback mechanism that matches an anonymous `session_key` to a database record to recover items if the session ID was lost or rotated.
- **Ghost Fallback**: Returns an unsaved `Basket` instance to provide a consistent API for the UI without bloating the database with empty records.

### 2. The Middleware (`basket/middleware.py`)

The `BasketMiddleware` acts as a global pre-processor. It invokes the Service Layer on every request and attaches the resulting object directly to the `request` object.

- **Global Accessibility**: By attaching the basket to the `request`, every view and template in the system has instant access to the current basket state.
- **Lazy Loading**: The middleware ensures that database hits only occur when the basket is actually accessed, maintaining high performance for static or non-commerce pages.

### 3. The Context Processor (`basket/context_processors.py`)

A custom context processor bridges the gap between the Middleware and the Django Template Engine. It passes `request.basket` into the global context, allowing the navigation partials to render the item count and total price on every page without redundant database queries.

## Membership & Subscriptions Pipeline

This section documents the asynchronous, event-driven subscription lifecycle engine implemented for the v2 Rebuild, which operates independently of the retail basket workflow.

### 1. Architectural Workflow

The membership modification and tracking architecture relies on out-of-band fulfilment to guarantee system resilience and prevent browser-side manipulation.

```
+------------------+       POST /membership/checkout/<id>/       +----------------------+
|  Client Browser  | -----------------------------------------> |  Django Application  |
+------------------+                                            +----------------------+
         |                                                                 |
         | (Native Redirect)                                               | stripe.checkout.Session.create()
         v                                                                 v
+------------------+                                            +----------------------+
| Stripe Checkout  |                                            |  Stripe API Servers  |
+------------------+                                            +----------------------+
         |                                                                 |
         | (Completes Payment)                                             |
         +---------------------------------------------------------------->| (Fires Event Async)
                                                                           |
                                                                           v
                                                                +----------------------+
                                                                |   /checkout/webhook/ |
                                                                +----------------------+
                                                                           |
                                                                           | to_dict_recursive()
                                                                           v
                                                                +----------------------+
                                                                | MembershipService    |
                                                                | .provision_tier()    |
                                                                +----------------------+
```

#### 1.1 Checkout Initiation

When an authenticated user requests a membership tier change, a secure `POST` request is sent to the backend. The `InitiateMembershipCheckoutView` resolves the targeted tier and delegates session creation to `MembershipService.create_checkout_session`.

During session creation:

- The system pairs a unique `stripe_customer_id` to the user record.
- Internal database primary keys (`user_id`, `tier_id`) are packed directly into the Stripe Checkout Session's immutable `metadata` dictionary.
- Absolute, dynamic callback URIs (`membership_success` and `membership_options`) are built using `request.build_absolute_uri()` to ensure strict path adherence across local and production environments.

#### 1.2 Hosted Checkout

The browser executes a native client-side redirect to Stripe's hosted billing interface. This offloads the entire PCI-DSS compliance scope, card validation, and authentication loops (such as 3D Secure verification) completely to Stripe.

#### 1.3 Webhook fulfilment

Upon successful payment, Stripe broadcasts an out-of-band `checkout.session.completed` event to the platform's public webhook route (`/checkout/webhook/`). Account access rights are modified asynchronously using the verified database primary keys contained within the metadata payload.

### 2. Defensive Engineering & Fault Tolerance

The integration architecture implements defensive programming measures to safeguard data pipelines from environment variations and mock testing side-effects.

#### 2.1 Recursive Payload Normalisation

Stripe SDK return values pass through custom object wrappers (`StripeObject`) that override standard magic methods. Direct lookups using dictionary-style `.get()` access patterns on un-normalised object structures trigger runtime `AttributeError` exceptions.

To achieve high fault tolerance, the webhook controller forces immediate recursive dictionary normalisation at the subsystem boundary:

```python
event_data = event.data.object.to_dict_recursive()
```

This guarantees that standard, non-crashing Python dictionary methods work reliably across all multi-layered event schemas.

#### 2.2 Isolated Exception Frameworks

When executing test runs via automated local tooling, mock data structures push non-numeric placeholder strings (e.g., `"prod_123"`) inside metadata payload dictionaries. The fulfilment logic handles this cleanly by separating database errors from formatting casting anomalies into distinct, explicit exception blocks:

```python
try:
    user = User.objects.get(pk=user_id)
    MembershipService.provision_tier(
        user=user,
        tier_id=int(tier_id),
    )
except ValueError:
    # Succinctly intercepts and discards Stripe CLI mock strings
    # without failing the server thread or throwing 500 status codes.
    pass
except User.DoesNotExist:
    # Catches situations where a metadata key is well-formed
    # but the matching user record is completely missing from the database.
    pass
```

#### 2.3 Environment-Aware Secret Toggling

To ensure zero manual code refactoring or risk of configuration leaks during integration or deployment cycles, the application settings utilize an automatic environment switch. The system evaluates the presence of hosting architecture flags (`IS_HEROKU_APP`) and selects the appropriate webhook signature validation token deterministically:

```python
if IS_HEROKU_APP:
    STRIPE_WH_SECRET = os.environ.get("STRIPE_WH")
else:
    STRIPE_WH_SECRET = os.environ.get("STRIPE_LOCAL_WH")
```

### 3. Local Development & Integration Verification

The integration infrastructure supports local testing workflows without requiring firewall modifications or public DNS proxy tools.

#### 3.1 Establish the Webhook Forwarding Tunnel

Execute the Stripe CLI listener to create a secure proxy link capable of intercepting webhooks from your developer account dashboard and redirecting them to your local Django server loop:

```bash
stripe listen --forward-to localhost:8000/checkout/webhook/
```

#### 3.2 Sync Signing Secrets

Upon execution, capture the unique local webhook signature token printed to the console:

```text
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Assign this string value directly to your local runtime parameters inside `env.py` under the environment key name **`STRIPE_LOCAL_WH`**.

#### 3.3 Trigger Simulated Event Pipelines

Open an independent terminal shell while your development server and tunnel are active, and dispatch a simulated subscription payload to verify your validation systems:

```bash
stripe trigger checkout.session.completed
```

Monitor your local Django execution server logs to confirm that all incoming transaction states process seamlessly and return uniform, healthy **`HTTP 200 OK`** response codes.

## App Structure

- `core`: Static pages, shared templates, site-wide UI concerns, HTMX integrations, and general platform behaviour.
- `accounts`: Authentication-adjacent account behaviour, dashboard access, `User`, and `MembershipTier`.
- `catalogue`: Product catalogue domain, including `Product`, `Category`, and `CategoryProductJoin`.
- `basket`: Temporary basket state and line items, including `Basket` and `Line`.
- `commerce`: Checkout, Stripe payment handling, completed orders, and `Order` / `OrderItem`.
- `warehouse`: Physical stock and fulfilment tracking, including `StockItem` and `HireRecord`.

### `core`

### `accounts`

### `catalogue`

### `commerce`

### `basket`

#### Overview

The `basket` app manages the temporary storage of products a user intends to purchase. It handles both authenticated users and anonymous guest sessions, acting as a bridge between the Catalogue and Commerce domains.

#### Key Implementation Details

- Identification: Uses `UUIDField` as primary key for `Basket` models to ensure session security and prevent ID enumeration.
- State Management: Implements a `Status` TextChoices class to track the lifecycle of a basket (`OPEN`, `MERGED`, `SAVED`, `SUBMITTED`).
- Data Persistence: The `Line` model captures the `price_at_addition`. This ensures that if a product's price changes in the Catalogue after being added, the customer's expected price is preserved until checkout.
- Relationships:
  - `Basket` belongs to a User (Optional).
  - `Line` links a `Basket` to a `Product` from the `Catalogue` app.
  - `unique_together` constraints on `Line` prevent duplicate entries for the same product in a single basket.

#### Logic, Mixins & Properties

To maintain modularity and avoid repetitive session lookups, the app utilizes a **BasketMixin** for all Class-Based Views (CBVs) that interact with user selections.

- **`BasketMixin.get_basket()`**:
  - Acts as the view-level gateway to the **Service Layer**.
  - Ensures that logic-heavy views (like `BasketUpdateView`) are using the exact same instance identified by the Middleware.
  - Guarantees architectural consistency: the View, the Middleware, and the Context Processor all point to the same "Single Source of Truth."

- `Line.line_reference`: A calculated property returning the subtotal for that specific line (Price × Quantity).
- `Basket.total_price`: A calculated property that aggregates all `line_reference` totals for a grand total.

---

### Deployment/Settings Note:

Ensure the middleware is registered in `settings.py` after `AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'basket.middleware.BasketMiddleware', # Global basket state provider
    ...
]
```

---

## API Specification

### Basket Update Contract

> [!NOTE]
> `total_price` is returned as a **formatted string** (e.g., `"£145.00"`) rather than a raw number. This ensures that the **Server** remains the single source of truth for currency symbols, locale-specific formatting, and decimal precision. This strategy prevents client-side floating-point errors (which JavaScript is famously poor at handling) and ensures a consistent, region-agnostic UI experience regardless of the user's browser settings.

### Scheme Definition

| Field       | Type    | Description                                                                |
| ----------- | ------- | -------------------------------------------------------------------------- |
| status      | string  | The result of the operation: `success` or `error`.                         |
| message     | string  | Human-readable feedback intended for UI Toast/Alert notifications.         |
| total_items | number  | The total count of items (or lines) currently in the basket.               |
| total_price | string  | The formatted total price, including currency symbol and 2 decimal places. |
| is_empty    | boolean | A helper flag to trigger "Empty Basket" UI states or redirects.            |

---

## Event Driven Architecture

The system utilizes a declarative, event-driven pattern to manage UI state and feedback, replacing manual JavaScript orchestration with a hybrid approach using **HTMX** and **Bootstrap**.

---

### 1. Request Lifecycle (The Payload)

All basket interactions—including adding, removing, and clearing items—are initiated via HTMX attributes defined directly on HTML elements.

- **Transport**: HTMX interceptors handle the `POST` request and automatically inject the `X-CSRFToken` into the headers.
- **Payload**: Data is transmitted as a JSON object using the `json-enc` extension to align with the requirements of the backend `BasketUpdateView`.
- **Session Management**: Each request explicitly refreshes the `basket_id` in the session, ensuring the browser and server stay synchronized and preventing session mismatches.

### 2. Signal Emission (The Backend)

The `BasketUpdateView` executes the business logic (updating the `Basket` and `Line` models) and communicates necessary UI changes back to the client via the `HX-Trigger` header.

- **Status Codes**: Successful updates return an `HTTP 204 No Content` to signal HTMX that no DOM swap is required .
- **Custom Headers**: The `HX-Trigger` header contains a JSON-encoded payload (e.g., `showToast`) containing a message and a status level (e.g., `success`, `danger`).

### 3. Notification Bridge (The Frontend)

A centralized listener in the JavaScript layer bridges the gap between server-side signals and client-side UI components.

- **Type Safety**: Custom events are handled via `JSDoc @typedef` definitions to ensure the integrity of the data payload passed from HTMX to the UI.
- **Consolidated UI**: All notifications, including those from the global error handler (`phReportError`) and manual scripts, are routed through a unified notification bridge to a Bootstrap `Toast` instance.

### 4. Implementation Matrix

| Action           | Trigger Mechanism  | Backend Logic     | UI Feedback Route     |
| :--------------- | :----------------- | :---------------- | :-------------------- |
| **Add Product**  | `hx-post` (ADD)    | `Basket.update()` | `showToast` (Success) |
| **Remove Item**  | `hx-post` (REMOVE) | `Line.delete()`   | `showToast` (Info)    |
| **Clear Basket** | `hx-post` (CLEAR)  | `Basket.clear()`  | `showToast` (Warning) |
| **System Error** | `phReportError()`  | Console Log       | `phNotify` (Danger)   |

---

## Authentication UI Architecture

This section outlines the architectural implementation used to unify `django-allauth` with the PropHouse industrial design system.

### 1. Form Strategy (`accounts/forms.py`)

To avoid adding unnecessary fields while still controlling the UI output, we extend the base Allauth forms to inject specific attributes.

#### Key Implementation:

- **Inheritance**: `CustomSignupForm(SignupForm)` and `CustomLoginForm(LoginForm)`.
- **Attribute Enrichment**: Widgets are updated in `__init__` to include `industrial-input` or `industrial-checkbox` classes.
- **Type Safety**: Use of `Dict[str, forms.Field]` type hints ensures editor autocomplete for widget and field attributes.
- **Contractual Attributes**: Explicitly setting `type` (e.g., `email`, `password`, `checkbox`) is required for the logic in the global element template.

### 2. Global Element Override (`templates/allauth/elements/field.html`)

The project utilizes Allauth's element system to create a single source of truth for field rendering.

#### Template Logic:

- **Contextual Rendering**: Uses `attrs.type` to distinguish between `textarea`, standard `input`, and `checkbox/radio`.
- **Layout Management**:
  - Text fields use top-aligned labels.
  - Checkboxes/Radios use `d-flex align-items-center gap-2` for side-by-side label alignment.
- **Variable Mapping**: Uses `{% with attrs=field.field.widget.attrs %}` to bridge the gap between Allauth's element variables and the custom industrial attribute system.

### 3. Implementation Matrix

| Page                   | Template Component     | Design Pattern                                           |
| :--------------------- | :--------------------- | :------------------------------------------------------- |
| **Signup**             | `{% element fields %}` | Vertical stack with industrial inputs.                   |
| **Login**              | `{% element fields %}` | Combined text inputs and industrial-styled checkbox.     |
| **Email Verification** | `industrial-container` | Informational block with standard industrial typography. |

<h3>4. UI/UX Standards</h3>

- **Interactivity**: All inputs use standard focus states defined in `core.css`.
- **Validation**: Error messages are rendered using the `industrial-error-msg` class within the field element.
- **Accessibility**: Semantic `<label>` tags are linked to inputs via `id_for_label` and `auto_id`.

---

## Security & Best Practice

- Environment variables for secrets.
- CSRF protection enabled.
- DEBUG disabled in production.
- Stripe webhooks validated.
- Atomic transactions used during checkout.

---

# Development & Code Style

## Git Commits

Conventional Commits format used for clear and structured history.

## Python

- PEP 8 compliant.
- Business logic separated into appropriate layers.
- Defensive validation of all user input.

## JavaScript

- Used for progressive enhancement only.
- No critical dependency on JS for core flows.

## HTMX

- **Declarative Interactions**: UI updates are driven by HTML attributes (`hx-post`, `hx-vals`, `hx-trigger`) rather than manual event listeners.
- **Event-Driven Feedback**: Utilizes `HX-Trigger` response headers to communicate backend state changes to the frontend notification system.
- **State Integrity**: All state-changing actions are routed through server-side views to ensure session and database synchronization.
- **Atomic Responses**: Preference for `204 No Content` or partial fragment swaps to maintain client-side DOM stability.
- **JSON Integration**: Uses the `json-enc` extension for consistent data exchange with Python-based business logic.

## HTML

- Semantic structure enforced.
- Accessible markup with ARIA where appropriate.

## CSS (BEM Methodology)

- Modular, predictable class naming.
- Clear separation of layout and component styles.

---

# Tools and Technologies

| Tool / Tech | Use                                   |
| ----------- | ------------------------------------- |
| Python      | Backend logic                         |
| Django      | Full-stack framework                  |
| PostgreSQL  | Relational database                   |
| Stripe      | Payment and subscription processing   |
| HTML        | Markup                                |
| CSS         | Styling                               |
| JavaScript  | Progressive enhancement               |
| HTMX        | Event-driven client-side architecture |
| Bootstrap   | Responsive layout                     |
| Git         | Version control                       |
| GitHub      | Repository hosting                    |

---

# Testing

See **TESTING.md** for full testing documentation.

---

# Deployment

> [!IMPORTANT]
> See [Current Limitations](#current-limitations) for details on why transactional emails are currently restricted to the admin address on the live Heroku site.

## Current Limitations

### Transactional Email Engine (Resend Sandbox Restrictions)

The app uses `django-anymail` and the **Resend API** to handle transactional emails. Because the live site is currently running in Resend's free sandbox mode without a custom domain, there are a few strict testing limits in place:

- **Emails only go to the admin:** Outbound emails sent from `onboarding@resend.dev` will _only_ deliver to the Resend account creator (**`robert.shelford@googlemail.com`**).

- **Other sign-ups will fail:** If you try to test the registration or email verification flows with any other email address, Resend's anti-spam filters will block it and throw an HTTP 403 validation error.

- **How to fix this for production:** To get normal email delivery working for everyone, you need to link a custom domain. This requires adding Resend’s MX and TXT records directly into your domain registrar's DNS settings (like Namecheap or GoDaddy). Verification cannot be achieved using Heroku’s automated `PointDNS` add-on zone files, as third-party hosting subdomains under the shared `herokuapp.com` Public Suffix List are globally restricted from domain ownership validation.

---

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full deployment instructions.

---

# Accessibility

PropHouse follows WCAG 2.1 AA guidelines, including:

- Keyboard-accessible navigation.
- Clear heading hierarchy.
- Accessible alerts and feedback.
- Colour contrast compliance.

---

# Credits

## Feature Credits

| Feature                                                            | Source                                                                                                           | Notes                                                         |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Stripe Integration                                                 | Stripe Documentation                                                                                             | Test mode implementation                                      |
| Authentication                                                     | Django Auth                                                                                                      | Standard auth system                                          |
| Event Driven Architecture                                          | [HTMX](https://htmx.org/docs/)                                                                                   |                                                               |
| [HTMX Responsive Form](core/templates/core/partials/_sidebar.html) | [HTMX - Active Search](https://htmx.org/examples/active-search)                                                  | Show live filter results without full page reload             |
| Hire status alert queries                                          | [Field lookups](https://docs.djangoproject.com/en/6.0/ref/models/querysets/#field-lookups)                       |                                                               |
|                                                                    |
| Reverse Admin URL Patterns                                         | [Django Docs: Reverse admin URLs](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#reversing-admin-urls) | Used to provide links between the various models within admin |

## Development Credits

| Development Feature         | Source                                                                                            | Notes |
| --------------------------- | ------------------------------------------------------------------------------------------------- | ----- | --- |
| Custom Management Commmands | [Django Docs](https://docs.djangoproject.com/en/6.0/howto/custom-management-commands/)            |       |
| Cloudinary SDK              | [Python Image & Video Upload](https://cloudinary.com/documentation/django_image_and_video_upload) |
|                             |                                                                                                   |       |     |

Used to perform advanced and related WHERE clause lookups on `HireRecord` model. |

## Acknowledgements

- Code Institute Level 5 Full Stack Development programme.

---

**Result:**

PropHouse is a relational database-backed Django application implementing secure e-commerce hire functionality with optional membership discounts, designed for a real-world production hire context.

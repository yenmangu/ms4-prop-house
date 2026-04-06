# PropHouse - Digital Hire Platform

## Live Application

- **Live site:** (To be added upon deployment)
- **Repository:** (GitHub repository link)
- **Documentation:** (GitHub README / Pages link if applicable)

---

## Overview

PropHouse is a digital hire platform designed for production companies and creative teams to browse, hire, and manage prop and equipment orders online.

All products are available for direct hire through a standard e-commerce checkout flow. In addition, users may subscribe to an optional membership plan which provides discounted pricing on eligible products. Membership enhances value through pricing benefits rather than gated access.

The core journey of the application is:

**Browse → Add to Basket → Checkout → Hire**

The platform is built using Django with a relational database and Stripe (test mode) for payment processing. It follows an accessibility-first, mobile-first approach aligned to WCAG 2.1 AA and the Code Institute Level 5 specification.

---

## Glossary

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
| Product Catalogue       | 01            | Must            | ⬜          |
| Product Detail          | 02            | Must            | ⬜          |
| Basket                  | 03            | Must            | ⬜          |
| Stripe Checkout         | 04            | Must            | ⬜          |
| Authentication          | 05            | Must            | ⬜          |
| Address Management      | 06            | Should          | ⬜          |
| Membership Subscription | 07            | Should          | ⬜          |

---

# Database Design

## Overview

PropHouse uses a relational database schema designed to support:

- A product catalogue with categories and stock tracking.
- A basket-to-checkout flow where orders are created only after successful payment.
- Membership subscriptions that apply percentage-based discounts to eligible products.
- Customer account features such as saved addresses (and optional wishlists).

### Stock Integrity Policy

- `Product.stock_quantity` is the authoritative stock value.
- Basket actions do **not** decrement database stock.
- Stock is decremented **only** during successful paid checkout.
- Checkout uses an atomic transaction and row-level locking (`select_for_update`) to prevent overselling.

This approach ensures stock remains consistent under concurrent checkouts.

---

## Entity Relationship Diagram

(ERD image / PlantUML diagram link)

---

## Schema Summary

### Relationship Overview

- **Category → Product**: One-to-many
- **User → Address**: One-to-many
- **User → Order**: One-to-many
- **Order → OrderItem**: One-to-many
- **Product → OrderItem**: One-to-many
- **User → Membership**: One-to-one (optional)
- **Membership → Subscription**: One-to-one (Stripe subscription record)
- **User ↔ Product (Wishlist)**: Many-to-many (optional)

---

## Models

### Product

Represents a hireable prop or equipment item.

Key fields:

- `name` (string)
- `slug` (unique string)
- `description` (text)
- `category` (FK → Category)
- `price` (decimal)
- `is_discount_eligible` (boolean)
- `stock_quantity` (integer)
- `featured_image` (image / Cloud storage reference)
- `is_active` (boolean)
- `created_on`, `updated_on` (datetimes)

Important constraints:

- `stock_quantity >= 0`
- `slug` unique

---

### Category

Groups products into browsable sections.

Key fields:

- `name` (string)
- `slug` (unique string)
- `description` (optional text)
- `is_active` (boolean)

---

### Order

Represents a completed hire transaction created after successful payment.

Key fields:

- `user` (FK → User)
- `order_number` (unique string)
- `status` (choice, e.g. `pending`, `paid`, `cancelled`, `refunded`)
- `stripe_payment_intent_id` (string)
- `stripe_checkout_session_id` (string)
- `full_name` (string)
- `email` (email)
- `phone_number` (optional string)
- `address_line_1`, `address_line_2`, `town_or_city`, `postcode`, `county`, `country` (strings)
- `original_basket` (text / JSON snapshot)
- `subtotal` (decimal)
- `discount_total` (decimal)
- `grand_total` (decimal)
- `created_on` (datetime)

Behaviour notes:

- An order is only marked `paid` after Stripe confirmation (often via webhook).
- The order stores a pricing snapshot to ensure totals remain auditable even if product prices change later.

---

### OrderItem

Represents an individual line item in an order.

Key fields:

- `order` (FK → Order)
- `product` (FK → Product)
- `quantity` (integer)
- `unit_price` (decimal)
- `line_total` (decimal)
- `discount_applied` (decimal)

Important constraints:

- `quantity >= 1`
- `line_total` calculated from `quantity * unit_price` minus discounts

---

### Address

A saved address record for a user (supports repeat checkout without re-entry).

Key fields:

- `user` (FK → User)
- `label` (string, e.g. “Studio”, “Office”)
- `full_name` (string)
- `phone_number` (optional string)
- `address_line_1`, `address_line_2`, `town_or_city`, `postcode`, `county`, `country` (strings)
- `is_default` (boolean)
- `created_on` (datetime)

Suggested constraints:

- Only one default address per user (enforced via application logic or conditional unique constraint).

---

### Membership

Represents a user’s membership status and discount entitlement.

Key fields:

- `user` (OneToOne → User)
- `is_active` (boolean)
- `discount_percent` (integer or decimal)
- `started_on` (datetime)
- `ended_on` (optional datetime)
- `stripe_customer_id` (string)

Behaviour notes:

- Membership modifies pricing (discount pricing) rather than access permissions.
- Discount is applied only to products flagged as discount-eligible.

---

### Subscription

Stores the Stripe subscription record mapped to a membership.

Key fields:

- `membership` (OneToOne → Membership)
- `stripe_subscription_id` (string)
- `stripe_price_id` (string)
- `status` (choice, e.g. `active`, `past_due`, `cancelled`)
- `current_period_end` (datetime)
- `cancel_at_period_end` (boolean)

---

### Wishlist (Optional)

Allows users to save products for later.

Implementation options:

- **Simple approach**: `User` ↔ `Product` M2M through a `WishlistItem` model.
- This supports metadata like timestamps and avoids a single shared wishlist per user.

Suggested fields (WishlistItem):

- `user` (FK → User)
- `product` (FK → Product)
- `created_on` (datetime)

---

## Data Operations Summary

The schema supports full CRUD across the core domain:

- Products: Create / Read / Update / Delete (admin managed).
- Categories: Create / Read / Update / Delete (admin managed).
- Addresses: Create / Read / Update / Delete (user managed).
- Basket: Session-based read/update operations (not persisted as orders).
- Orders: Created on successful checkout; viewable by the owning user; managed by staff.
- Membership/Subscription: Created and updated via Stripe events and user actions.

---

# Architecture

## High-Level Overview

- Django templates for server-side rendering.
- Django ORM for relational data modelling.
- Stripe test API for payments and subscriptions.
- Modular apps aligned to domain boundaries.

## App Structure

- core (static pages, base templates)
- accounts (authentication, dashboard)
- profiles (addresses, wishlist if implemented)
- catalogue (products, categories)
- commerce (checkout, orders, subscription logic)
- basket (basket and lines)

### `core`

### `accounts`

### `profiles`

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

To maintain modularity and avoid repetitive session lookups, the app utilizes a BasketMixin for all Class-Based Views (CBVs) that interact with user selections.

- `BasketMixin.get_basket()`:
  - Checks the `request.session` for an existing `basket_id`.
  - Validates that the basket is still in an `OPEN` state.
  - If no valid basket is found (e.g., a new guest or an expired session), it invokes `_create_basket()`.
- `BasketMixin._create_basket()`:
  - Instantiates a new `Basket` model.
  - Securely stores the `UUID` as a string in the session to persist the guest's state.
- User Merging Logic: (Planned) Handles the transition of an anonymous guest basket to a `User` account upon login, ensuring no items are lost during authentication.

- `Line.line_reference`: A calculated property returning the subtotal for that specific line (Price $\times$ Quantity).
- `Basket.total_price`: A calculated property that aggregates all `line_reference` totals for a grand total.

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

## HTML

- Semantic structure enforced.
- Accessible markup with ARIA where appropriate.

## CSS (BEM Methodology)

- Modular, predictable class naming.
- Clear separation of layout and component styles.

---

# Tools and Technologies

| Tool / Tech | Use                                 |
| ----------- | ----------------------------------- |
| Python      | Backend logic                       |
| Django      | Full-stack framework                |
| PostgreSQL  | Relational database                 |
| Stripe      | Payment and subscription processing |
| HTML        | Markup                              |
| CSS         | Styling                             |
| JavaScript  | Progressive enhancement             |
| Bootstrap   | Responsive layout                   |
| Git         | Version control                     |
| GitHub      | Repository hosting                  |

---

# Testing

See **TESTING.md** for full testing documentation.

---

# Deployment

See **DEPLOYMENT.md** for full deployment instructions.

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

| Feature            | Source               | Notes                    |
| ------------------ | -------------------- | ------------------------ |
| Stripe Integration | Stripe Documentation | Test mode implementation |
| Authentication     | Django Auth          | Standard auth system     |

## Development Credits

| Development Feature         | Source                                                                                            | Notes |
| --------------------------- | ------------------------------------------------------------------------------------------------- | ----- |
| Custom Management Commmands | [Django Docs](https://docs.djangoproject.com/en/6.0/howto/custom-management-commands/)            |       |
| Cloudinary SDK              | [Python Image & Video Upload](https://cloudinary.com/documentation/django_image_and_video_upload) |       |

## Acknowledgements

- Code Institute Level 5 Full Stack Development programme.

---

**Result:**

PropHouse is a relational database-backed Django application implementing secure e-commerce hire functionality with optional membership discounts, designed for a real-world production hire context.

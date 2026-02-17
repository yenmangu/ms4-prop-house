# Database Design

## Overview

PropHouse uses a relational database schema designed to support:

- A product catalogue with category grouping and stock tracking.
- A basket-to-checkout flow where orders are created only after
  successful payment.
- Membership plans that define discount offers.
- User memberships that grant discount entitlements.
- Stripe-backed subscriptions that fund memberships.
- Customer account features such as saved addresses (and optional
  wishlists).

---

## Stock Integrity Policy

- `Product.stock_quantity` is the authoritative stock value.
- Basket actions do **not** decrement database stock.
- Stock is decremented **only** during successful paid checkout.
- Checkout uses an atomic transaction and row-level locking
  (`select_for_update`) to prevent overselling.

This approach ensures stock remains consistent under concurrent
checkouts.

---

## Entity Relationship Overview (Locked Schema)

### Core Relationships

- **Product ↔ Category**: Many-to-many (via `ProductCategoryLink`)
- **User → Address**: One-to-many
- **User → Order**: One-to-many
- **Order → OrderItem**: One-to-many
- **Product → OrderItem**: One-to-many
- **User → Membership**: One-to-many (optional; preserves history)
- **Membership → MembershipPlan**: Many-to-one
- **Membership → Subscription**: One-to-one (Stripe billing record)
- **User ↔ Product (Wishlist)**: Many-to-many (optional)

---

## Models

### Product (catalogue app)

Represents a hireable prop or equipment item.

Key fields:

- `name`
- `slug` (unique)
- `description`
- `price`
- `is_discount_eligible`
- `stock_quantity`
- `featured_image`
- `is_active`
- `created_on`, `updated_on`

Notes:

- A product may belong to multiple categories.
- `stock_quantity >= 0`
- `slug` is unique.

---

### Category (catalogue app)

Groups products into browsable sections.

Key fields:

- `name`
- `slug` (unique)
- `description`
- `is_active`

---

### ProductCategoryLink (catalogue app)

Join table for Product ↔ Category many-to-many relationship.

Key fields:

- `product` (FK → Product)
- `category` (FK → Category)

---

### Order (commerce app)

Represents a completed hire transaction created after successful
payment.

Key fields:

- `user` (FK → User)
- `order_number` (unique)
- `status`
- `stripe_payment_intent_id`
- `email`
- Shipping snapshot fields:
  - `shipping_full_name`
  - `shipping_phone_number`
  - `shipping_address_line_1`
  - `shipping_address_line_2`
  - `shipping_city`
  - `shipping_county`
  - `shipping_post_code`
  - `shipping_country`
- Financial snapshot:
  - `original_basket_snapshot`
  - `membership_discount_at_purchase`
  - `subtotal`
  - `discount_total`
  - `grand_total`
- `created_on`, `updated_on`

Behaviour notes:

- Orders store a full pricing and shipping snapshot.
- Historical integrity is preserved even if product prices or
  membership plans change.

---

### OrderItem (commerce app)

Represents an individual line item in an order.

Key fields:

- `order` (FK → Order)
- `product` (FK → Product)
- `quantity`
- `unit_price`
- `line_total`
- `discount_applied`

Constraints:

- `quantity >= 1`
- `line_total` derived from quantity and price minus discount.

---

### Address (profiles app)

A saved user address used for checkout autofill.

Key fields:

- `user` (FK → User)
- `address_line_1`
- `address_line_2`
- `city`
- `county`
- `post_code`
- `country`

Notes:

- Used to prepopulate checkout.
- Order stores its own snapshot copy.

---

### MembershipPlan (catalogue app)

Defines a membership offer available for purchase.

Represents the catalogue definition of a membership.

Key fields:

- `name`
- `description`
- `discount_to_apply`
- `unit_cost`
- `is_active` (recommended)

Example:

"Gold Membership --- 10% off eligible products"

---

### Membership (accounts app)

Represents a user's entitlement instance.

Each membership record links a user to a membership plan.

Key fields:

- `user` (FK → User)
- `membership_plan` (FK → MembershipPlan)
- `is_active`
- `discount_percent` (snapshot of plan discount at activation)
- `started_on`
- `end_on`

Notes:

- A user may have zero or many memberships (history preserved).
- Only one membership should be active at a time (application logic).

---

### Subscription (commerce app)

Represents the Stripe billing contract backing a membership.

Key fields:

- `membership` (FK → Membership)
- `stripe_subscription_id`
- `stripe_price_id`
- `status`
- `current_period_end`
- `cancel_at_period_end`

Notes:

- Subscription manages billing lifecycle.
- Membership manages entitlement lifecycle.

---

### Wishlist (optional, profiles app)

Allows users to save products.

Implementation via join model:

- `user` (FK → User)
- `product` (FK → Product)
- `created_on`

---

## Data Operations Summary

- Products, Categories, MembershipPlans: Admin CRUD.
- Addresses: User CRUD.
- Basket: Session-based (not persisted as Order).
- Orders: Created after successful Stripe confirmation.
- Memberships: Created/updated via subscription lifecycle.
- Subscriptions: Synced from Stripe webhooks.

---

## App Ownership Summary

- `catalogue`: Product, Category, ProductCategoryLink, MembershipPlan
- `commerce`: Order, OrderItem, Subscription
- `profiles`: Address (and optional Wishlist)
- `accounts`: Membership

This structure cleanly separates:

- What can be purchased (catalogue)
- What was purchased (commerce)
- What a user is entitled to (accounts)
- What a user stores (profiles)

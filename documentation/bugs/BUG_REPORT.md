> [!NOTE]
> Return back to the [README.md](/README.md) file.

## Incident Report: Basket Session Persistence

**Date:** 2026-05-01
**Project Phase:** Basket & Session Development
**Status:** Resolved

### 1. The Problem

During automated testing, a basket session persistence test revealed that guest baskets could be created before a session key existed, preventing reliable basket recovery on subsequent requests.

### 2. Root Cause Analysis

The basket lookup and creation logic was executing before the Django session had been initialised, meaning no session key was available to associate with the basket. This caused the basket to be orphaned and unrecoverable for the remainder of the session.

### 3. Resolution Steps

The fix ensured that a session was explicitly created and a session key generated before any basket lookup or creation was attempted. This guaranteed that the basket was always associated with a valid, persistent session key.

### 4. Impact

Resolved unreliable basket recovery for guest users and provided confidence that session-basket association behaves correctly across requests.

---

## Incident Report: Address Model Import in Service Layer

**Date:** 2026-05-15
**Project Phase:** Saved Address Feature Development
**Status:** Resolved

### 1. The Problem

During implementation of the saved-address feature, address service tests exposed a runtime error where the `Address` model was not imported correctly within the service layer, causing failures when attempting to validate or persist address data.

### 2. Root Cause Analysis

The `Address` model import was missing or incorrectly referenced within the address service module. The error was not immediately visible from the view layer but surfaced as soon as the service was exercised directly through unit tests.

### 3. Resolution Steps

Tests were written to validate:

- Valid address data passes form validation.
- Invalid address data returns validation errors.
- Default addresses can be saved successfully.
- Existing default addresses are replaced correctly.

The failing test identified the defect immediately. The import was corrected in the service layer before integration into the checkout workflow.

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

### 4. Impact

The failing test identified the defect before it could propagate into the checkout workflow. This reinforced the value of service-layer testing as an early warning system for integration issues.

---

## Incident Report: Database Migration & Schema Desync

**Date:** 2026-05-11
**Project Phase:** Hire Flow Development
**Status:** Resolved

### 1. The Problem

While developing the hire flow, a `ProgrammingError` was triggered when accessing the **HireRecord** Admin page. The error specifically cited that the column `commerce_orderitem.product_name` did not exist.

This was architecturally significant because the `HireRecordAdmin` uses `list_select_related` to join `OrderItem` and `Order`. When Django performed the SQL `JOIN`, it attempted to fetch all columns for `OrderItem`; the physical absence of `product_name` in the database caused the query to fail.

### 2. Root Cause Analysis

A migration desync occurred between the Django migration history and the physical PostgreSQL schema:

- **Migration 0003** was marked as **Applied [X]** in the migration history.
- However, the physical table `commerce_orderitem` was missing the columns defined in that migration (`product_name`, `production_name`, `start_date`, `end_date`).
- Additionally, an orphaned table `commerce_orderline` (slated for deletion in migration `0003`) still existed in the database, blocking a clean re-run of the migration logic.

### 3. Resolution Steps

The reconciliation was performed manually to align the physical database with the codebase:

1. **Manual Table Removal**: Accessed `dbshell` to manually drop the orphaned `commerce_orderline` table.
2. **Schema Alignment**: Successfully re-applied migrations `0003` and `0004` to physically add the missing snapshot columns to the `OrderItem` table.
3. **Admin Restoration**: Confirmed the columns existed and re-enabled `list_select_related` in `admin.py` to restore optimized query performance.

### 4. Technical References

- **Fix Commit:** `c5eae496e52145b78db5b28b073c046d0a8cb508` (Reconciled schema and restored joins)
- **Flag Commit:** `a95c8439de637aacd3590bcba9278821213d9f82` (Empty commit for documentation audit trail)

---

#### Impact on Architecture

This resolution solidifies the **Domain Separation** between `Commerce` (Financial snapshots) and `Warehouse` (Physical assets). By ensuring `OrderItem` correctly captures logistical snapshots (`product_name`, `start_date`, `end_date`), the system can now safely handle the upcoming **Stripe integration** without historical data corruption.

---

## Incident Report: Duplicate HTMX Requests from Responsive Filter Forms

**Date:** 2026-06-12
**Project Phase:** Final QA & Search Refinement
**Status:** Resolved

### 1. The Problem

During testing of the catalogue search functionality, HTMX search requests appeared to behave inconsistently.

Symptoms included:

- The search query briefly appearing in the URL before reverting to `?q=`.
- Search results flashing but not updating correctly.
- Correct results only appearing after additional browser interactions such as changing focus.

Heroku logs revealed that two requests were being generated for a single search action:

```text
GET /?q=oil
GET /?q=
```

The empty request consistently overwrote the valid search request, resulting in stale results being displayed.

### 2. Root Cause Analysis

Initial investigation identified that both the desktop and mobile filter forms were active simultaneously.

A form synchronisation system was implemented to enable only the currently active form and disable the inactive responsive variant. However, the fix appeared ineffective because JavaScript was unable to locate either form.

Further inspection revealed a template bug in the form ID generation:

```html
id="{% if mobile %} sidebar-form-mobile {% else %} sidebar-form-desktop {% endif
%}"
```

The rendered HTML therefore contained leading and trailing whitespace inside the ID attribute:

```html
id=" sidebar-form-desktop "
```

As a result:

```js
document.querySelector('#sidebar-form-desktop');
```

returned `null`, preventing the form synchronisation logic from executing.

### 3. Resolution Steps

1. Confirmed duplicate HTMX requests via browser network tools and Heroku logs.
2. Identified that both responsive filter forms were generating requests.
3. Added form synchronisation logic to enable only the active responsive form.
4. Discovered the malformed template-generated IDs through DevTools inspection and direct DOM queries.
5. Removed the unintended whitespace from the template:

```html
id="{% if mobile %}sidebar-form-mobile{% else %}sidebar-form-desktop{% endif %}"
```

6. Verified that JavaScript could correctly locate both forms and that only a single HTMX request was generated for each search action.

### 4. Technical References

- Affected Components:
  - Core filter forms
  - HTMX search integration
  - Responsive sidebar/off-canvas filters
  - `syncForms.js`

- **Fix Commit:** `8ccaa268bb419801aaa0334000ae752815983eec`

---

#### Impact on Architecture

This fix improved the reliability of the catalogue search experience and reinforced the responsive architecture used by the filtering system.

The incident also highlighted the importance of validating template-generated identifiers when JavaScript behaviour depends on DOM element lookup. Although the rendered markup appeared visually correct in DevTools, leading and trailing whitespace within the ID attribute prevented CSS selectors and DOM queries from matching the expected elements.

#### Further Reading

While the bug itself was relatively small, the investigation resulted in a more robust responsive form architecture. The full design process, including the abstraction layers used to model filter ownership and synchronisation, is documented separately:

- [Filter State Synchronisation](./filter_state.md)

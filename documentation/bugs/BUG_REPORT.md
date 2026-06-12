> [!NOTE]
> Return back to the [README.md](/README.md) file.

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
  - Catalogue filter forms
  - HTMX search integration
  - Responsive sidebar/off-canvas filters
  - `syncForms.js`

---

#### Impact on Architecture

This fix improved the reliability of the catalogue search experience and reinforced the responsive architecture used by the filtering system.

The incident also highlighted the importance of validating template-generated identifiers when JavaScript behaviour depends on DOM element lookup. Although the rendered markup appeared visually correct in DevTools, leading and trailing whitespace within the ID attribute prevented CSS selectors and DOM queries from matching the expected elements.

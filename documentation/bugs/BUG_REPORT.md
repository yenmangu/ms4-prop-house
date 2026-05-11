> [!NOTE]
> Return back to the [README.md](/README.md) file.

## Incident Report: Database Migration & Schema Desync

**Date:** 2026-05-11
**Project Phase:** Hire Flow Development
**Status:** Resolved

---

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

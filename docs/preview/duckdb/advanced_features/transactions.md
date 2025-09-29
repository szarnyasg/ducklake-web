---
layout: docu
title: Transactions
---

DuckLake has full support for [ACID](https://en.wikipedia.org/wiki/ACID) and offers snapshot isolation for all interactions with the database.
All operations, including DDL statements such as `CREATE TABLE` or `ALTER TABLE`, have full transactional support.
Transactions have all-or-nothing semantics and can be composed of multiple changes that are made to the database.

The extension also provides some syntax to be able to manage transactions. This is explained in the [DuckDB documentation](https://duckdb.org/docs/stable/sql/statements/transactions). Basically it comes down to this:

```sql
BEGIN TRANSACTION;
-- Some operation
-- Some other operation
COMMIT;
-- Or
ROLLBACK; -- ABORT will have the same behavior
```

In the context of DuckLake, one committed transaction (i.e., a `BEGIN-COMMIT` block) represents one [snapshot]({% link docs/preview/duckdb/usage/snapshots.md %}).

If multiple transactions are being performed concurrently in one table, the `ducklake` extension has some default configurations for a retry mechanism. This default configurations can be [overridden]({% link docs/preview/duckdb/usage/configuration.md %}).

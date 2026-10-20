---
layout: docu
title: Time Travel
---

In DuckLake, every [snapshot]({% link docs/stable/duckdb/usage/snapshots.md %}) represents a consistent state of the database.
DuckLake keeps a record of all historic snapshots and their changesets, unless historic snapshots are explicitly [expired]({% link docs/stable/duckdb/maintenance/expire_snapshots.md %}).

Using time travel, it is possible to query the state of the database as of any recorded snapshot.
The snapshot to query can be specified either (1) using a timestamp, or (2) explicitly using a snapshot identifier.
The `snapshots` function can be used to obtain a list of valid snapshots for a given DuckLake database.

Future timestamps are rejected.
Inside a transaction, time travel excludes uncommitted changes and cannot read snapshots committed after the transaction's snapshot.

## Examples

Query the table at a specific snapshot version.

```sql
SELECT * FROM tbl AT (VERSION => 3);
```

Query the table as it was last week.

```sql
SELECT * FROM tbl AT (TIMESTAMP => now() - INTERVAL '1 week');
```

Attach a DuckLake database at a specific snapshot version.

```sql
ATTACH 'ducklake:metadata.duckdb' (SNAPSHOT_VERSION 3);
```

Attach a DuckLake database as it was at a specific time.

```sql
ATTACH 'ducklake:metadata.duckdb' (SNAPSHOT_TIME '2025-05-26 00:00:00');
```

---
layout: docu
title: Data Inlining
---

When writing small changes to DuckLake, it can be wasteful to write each changeset to an individual Parquet file.
DuckLake supports directly writing small changes to the metadata using _data inlining_.
Instead of writing a Parquet file to the data storage and then writing a reference to that file in the metadata catalog, we directly write the rows to inlined data tables within the metadata catalog.

Data inlining can be enabled in two ways:

Using the `DATA_INLINING_ROW_LIMIT` attach parameter. This is bounded to your DuckLake connection, so if you detach and reattach without the parameter, data inlining won't be used.

```sql
ATTACH 'ducklake:inlining.duckdb' AS my_ducklake (DATA_INLINING_ROW_LIMIT 10);
```

Using the option `data_inlining_row_limit` which can be set at the table, schema or global level. This is persisted in the `ducklake_metadata` table and will be reused across connections.

```sql
ATTACH 'ducklake:inlining.duckdb' AS my_ducklake;
USE my_ducklake;
CREATE TABLE t (a INT);
CALL my_ducklake.set_option('data_inlining_row_limit', 10, table_name => 't');
```

When enabled, any inserts that write fewer than the given amount of rows are automatically written to inlined tables instead.

Inlined data behaves exactly the same as data written to Parquet files.
The only difference is that the inlined data lives in the metadata catalog, instead of in Parquet files in the data path.

For example, when inserting a low number of rows, data is automatically inlined:

```sql
CREATE TABLE my_ducklake.tbl (col INTEGER);
-- Inserting 3 rows, data is inlined
INSERT INTO my_ducklake.tbl VALUES (1), (2), (3);
-- No Parquet files exist
SELECT count(*) FROM glob('inlining.duckdb.files/**');
```

```text
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│      0       │
└──────────────┘
```

When inserting more data than the `DATA_INLINING_ROW_LIMIT`, inserts are automatically written to Parquet:

```sql
INSERT INTO my_ducklake.tbl FROM range(100);
SELECT count(*) FROM glob('inlining.duckdb.files/**');
```

```text
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│      1       │
└──────────────┘
```

## Metadata Catalog Support

Data inlining is supported when using DuckDB, PostgreSQL or SQLite as the metadata catalog.

When using a non-DuckDB metadata catalog, nested types (`STRUCT`, `MAP` and `LIST`) are stored as `VARCHAR` strings in the inlined data table. DuckLake automatically casts the values back to the correct type when reading.

## Flushing Inlined Data

Inlined data can be manually flushed to Parquet files by calling the `ducklake_flush_inlined_data` function.

Flush all inlined data in all schemas and tables:

```sql
CALL ducklake_flush_inlined_data('my_ducklake');
```

Flush inlined data only within a specific schema:

```sql
CALL ducklake_flush_inlined_data(
    'my_ducklake',
    schema_name => 'my_schema'
);
```

Flush inlined data for a specific table in the default `main` schema:

```sql
CALL ducklake_flush_inlined_data(
    'my_ducklake',
    table_name => 'my_table'
);
```

Flush inlined data for a specific table in a specific schema:

```sql
CALL ducklake_flush_inlined_data(
    'my_ducklake',
    schema_name => 'my_schema',
    table_name => 'my_table'
);
```

### Time Travel and Deletions

When flushing inlined data that has had rows deleted, DuckLake creates both the materialized Parquet data file and a corresponding deletion file. The deletion file records which rows were deleted and at which snapshot, preserving full time-travel support for the flushed data.

For example:

```sql
ATTACH 'ducklake:inlining.duckdb' AS my_ducklake (DATA_PATH 'data/', DATA_INLINING_ROW_LIMIT 10);
USE my_ducklake;

CREATE TABLE t1 (a INTEGER);
INSERT INTO t1 VALUES (1), (2), (3), (4), (5), (6), (7), (8);

DELETE FROM t1 WHERE a = 2;
DELETE FROM t1 WHERE a = 5;

-- Flush materializes data to Parquet and creates a deletion file with snapshot information
CALL ducklake_flush_inlined_data('ducklake');
```

After flushing, time travel to snapshots before the deletions still returns the deleted rows:

```sql
-- Returns all 8 original rows
SELECT * FROM t1 AT (VERSION => 1);
```

### Interaction with `auto_compact`

If a table has `auto_compact` set to `false`, `ducklake_flush_inlined_data` will skip it when flushing the whole lake or a whole schema. The same applies when flushing via `CHECKPOINT`, since `CHECKPOINT` calls `ducklake_flush_inlined_data` internally.

> **Note** `auto_compact` does not cause flushing to happen automatically after writes. It only determines whether a table is eligible for flushing when a maintenance function is called.

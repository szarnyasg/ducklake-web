---
layout: docu
title: DuckDB to DuckLake
---

Migrating from DuckDB to DuckLake is very simple to do with the DuckDB DuckLake extension. However, if you are currently using some DuckDB features that are [unsupported in Ducklake]({% link docs/preview/duckdb/unsupported_features.md %}), this guide will definitely help you.

## First Scenario: Everything is Supported

If you are not using any of the unsupported features, migrating from DuckDB to Ducklake will be as simple as running the following commands:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;
ATTACH 'duckdb.db' AS my_duckdb;

COPY FROM DATABASE my_duckdb TO my_ducklake;
```

Note that it doesn't matter what catalog you are using as a metadata backend for DuckLake.

## Second Scenario: Not Everything is Supported

If you have been using DuckDB for a while, there is a chance you are using some very specific types, macros, default values that are not literals or even things like generated columns. If this is your case, then migrating will have some tradeoffs.

- Specific types need to be casted to a [supported DuckLake type]({% link docs/preview/specification/data_types.md %}). User defined types that created as a `STRUCT` can be interpreted as such and `ENUM` can be usually casted to a type. `UNION`, on the other hand, is hard to cast and is left out of scope.

- Macros can be migrated to a DuckDB persisted database. If you are using DuckDB as your catalog for DuckLake, then this will be the destination. If you are using other catalogs like PostgreSQL, SQLite or MySQL, DuckDB macros are not supported and therefore can't be migrated.

- Default values that are not literals require that you change the logic of your insertion. See the following example:

```sql
-- Works in DuckDB, doesn't work in Ducklake
CREATE TABLE t1 (id INTEGER, d DATE DEFAULT now());
INSERT INTO t1 VALUES (2);

-- Works in Ducklake and simulates the same behaviour
CREATE TABLE t1 (id INTEGER, d DATE);
INSERT INTO t1 VALUES(2, now());
```

- Generated columns are the same as defaults that are not literals and therefore they need to be specified when inserting the data into the destination table. That means that the values will always be persisted (no `VIRTUAL` option).
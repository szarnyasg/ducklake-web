---
layout: docu
title: Logging
---

DuckDB provides a [logging framework](https://duckdb.org/docs/current/operations_manual/logging/overview) that can be used to debug and monitor DuckLake operations. The DuckLake extension registers a dedicated log type for metadata queries, and DuckDB's built-in `QueryLog` type can be used to trace all SQL queries including those issued internally by the extension.

## DuckLake Metadata Query Log

Metadata queries can be an important factor in performance, especially when using a remote catalog (e.g., PostgreSQL). The DuckLake extension registers the `DuckLakeMetadata` log type, which logs every metadata query together with timing information.

### Enabling the Log

```sql
CALL enable_logging('DuckLakeMetadata');
```

### Log Fields

`DuckLakeMetadata` is a structured log type. Use `duckdb_logs_parsed` to query the individual fields directly:

| Field | Type | Description |
|---|---|---|
| `catalog` | `VARCHAR` | The name of the DuckLake catalog that issued the query |
| `query` | `VARCHAR` | The metadata SQL query that was executed against the catalog database |
| `elapsed_ms` | `BIGINT` | The time the query took to execute, in milliseconds |

### Example

```sql
ATTACH 'ducklake:catalog.db' AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;
CREATE TABLE t1 (a INTEGER, b VARCHAR);

-- Enable DuckLake metadata logging
CALL enable_logging('DuckLakeMetadata');

-- Run an operation that triggers metadata queries
INSERT INTO t1 VALUES (1, 'hello'), (2, 'world');

-- View the metadata queries with structured fields
SELECT catalog, elapsed_ms, query
FROM duckdb_logs_parsed('DuckLakeMetadata');
```

## DuckDB Query Log

DuckDB's built-in `QueryLog` type logs every query executed on every connection, including the internal queries that the DuckLake extension issues against the catalog database. This can be useful for general debugging or to see the full picture of what DuckLake does under the hood.

### Enabling the Log

```sql
CALL enable_logging('QueryLog');
```

### Example

```sql
ATTACH 'ducklake:catalog.db' AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;
CREATE TABLE t1 (a INTEGER, b VARCHAR);

-- Enable query logging
CALL enable_logging('QueryLog');

-- Run an operation
INSERT INTO t1 VALUES (1, 'hello');

-- View all queries including internal DuckLake metadata queries
SELECT type, message
FROM duckdb_logs
WHERE type = 'QueryLog';
```

## Combining Log Types

Both log types can be enabled simultaneously to get DuckLake-specific timing information alongside the full query trace:

```sql
CALL enable_logging(['DuckLakeMetadata', 'QueryLog']);
```

## Logging to Different Storages

By default, logs are stored in an in-memory buffer and queried via the `duckdb_logs` view. DuckDB also supports logging to stdout or to a file:

```sql
-- Log to stdout
CALL enable_logging('DuckLakeMetadata', storage = 'stdout');

-- Log to a file
CALL enable_logging('DuckLakeMetadata', storage_path = '/tmp/ducklake_logs');
```

For more details on log storages and advanced configuration, see the [DuckDB Logging documentation](https://duckdb.org/docs/current/operations_manual/logging/overview).

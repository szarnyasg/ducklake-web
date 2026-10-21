---
layout: docu
title: Deletion Vectors
---

> Warning Writing deletion vectors is experimental.

DuckLake can record deleted row positions using Iceberg V3 deletion vectors in `.puffin` files instead of Parquet positional delete files.
The `write_deletion_vectors` option is disabled by default.

## Examples

Enable deletion vectors when attaching a catalog:

```sql
ATTACH 'ducklake:deletions.ducklake' AS my_ducklake
    (WRITE_DELETION_VECTORS true, DATA_INLINING_ROW_LIMIT 0);
USE my_ducklake;
CREATE TABLE tbl AS SELECT i AS id FROM range(100) t(i);
DELETE FROM tbl WHERE id = 0;
```

The `WRITE_DELETION_VECTORS` attach option is not persisted and must be specified on each attach.

The option can also be set per table:

```sql
ALTER TABLE tbl SET (write_deletion_vectors = true);
```

The `write_deletion_vectors` option set with `set_option` or `ALTER TABLE ... SET` is stored in the catalog.

With [data inlining]({% link docs/stable/duckdb/advanced_features/data_inlining.md %}) enabled, small deletions can remain in the metadata catalog until flushed.
`ducklake_flush_inlined_data` also uses the configured delete file format.

In DuckLake format version 1.1, deletions from multiple snapshots of the same data file can be consolidated into one Puffin file while retaining the snapshot information needed for [time travel]({% link docs/stable/duckdb/usage/time_travel.md %}) and the [data change feed]({% link docs/stable/duckdb/advanced_features/data_change_feed.md %}).
Catalogs pinned to format version 1.0 fall back to Parquet delete files for deletions spanning multiple snapshots.

Puffin deletion-vector files are written without encryption, including when the catalog was initialized with [`ENCRYPTED`]({% link docs/stable/duckdb/advanced_features/encryption.md %}).

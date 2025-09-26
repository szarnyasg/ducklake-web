---
layout: docu
title: Paths
---

DuckLake manages files stored in a separate storage location.
The paths to the files are stored in the catalog server.
Paths can be either absolute or relative to their parent path.
Whether or not a path is relative is stored in the `path_is_relative` column, alongside the `path`.
By default, all paths written by DuckLake are relative paths.

| Path type   | Path location                                 | Parent path |
| ----------- | --------------------------------------------- | ----------- |
| File path   | `ducklake_data_file` / `ducklake_delete_file` | Table path  |
| Table path  | `ducklake_table`                              | Schema path |
| Schema path | `ducklake_schema`                             | Data path   |
| Data path   | `ducklake_metadata`                           |             |

## Default Path Structure

The root `data_path` is specified through the [`data_path` parameter]({% link docs/stable/duckdb/usage/connecting.md %}) when creating a new DuckLake.
When loading an existing DuckLake, the `data_path` is loaded from the `ducklake_metadata` if not provided.

**Schemas.** When creating a schema, a schema path is set. By default, this path is the name of the schema for alphanumeric names (`⟨schema_name⟩/`{:.language-sql .highlight}) – or `⟨schema_uuid⟩/`{:.language-sql .highlight} otherwise.
This path is set as relative to the root `data_path`.

**Tables.** When creating a table, a table path is set. By default, this path is the name of the schema for alphanumeric names (`⟨table_name⟩⟩/`{:.language-sql .highlight}) – or `⟨table_uuid⟩/`{:.language-sql .highlight} otherwise.
This path is set as relative to the path of the parent schema.

**Files.** When writing a new data or delete file to the table, a new file path is generated.
For unpartitioned tables, this path is `ducklake-⟨uuid⟩.parquet`{:.language-sql .highlight} – relative to the table path.

**Partitioned Files.** When writing data to a partitioned table, the files are by default written to directories in the [Hive partitioning style](https://duckdb.org/docs/stable/data/partitioning/hive_partitioning#hive-partitioning).
Writing data in this manner is not required as the partition values are tracked in the catalog server itself.

This results in the following path structure:

```sql
main
├── unpartitioned_table
│   └── ducklake-⟨uuid⟩.parquet
└── partitioned_table
	└── year=2025
	    └── ducklake-⟨uuid⟩.parquet
```

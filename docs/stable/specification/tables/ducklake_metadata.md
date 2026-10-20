---
layout: docu
title: ducklake_metadata
---

The `ducklake_metadata` table contains key/value pairs with information about the specific setup of the DuckLake catalog.

| Column name | Column type |            |
| ----------- | ----------- | ---------- |
| `key`       | `VARCHAR`   | Not `NULL` |
| `value`     | `VARCHAR`   | Not `NULL` |
| `scope`     | `VARCHAR`   |            |
| `scope_id`  | `BIGINT`    |            |

- `key` is an arbitrary key string. See below for a list of pre-defined keys. The key cannot be `NULL`.
- `value` is the arbitrary value string. The `value` cannot be `NULL`.
- `scope` defines the scope of the setting.
- `scope_id` is the id of the item that the setting is scoped to (see the table below) or `NULL` for the Global scope.

| Scope  | `scope`  | Description                                                        |
| ------ | -------- | ------------------------------------------------------------------ |
| Global | `NULL`   | The scope of the setting is global for the entire catalog.         |
| Schema | `schema` | The setting is scoped to the `schema_id` referenced by `scope_id`. |
| Table  | `table`  | The setting is scoped to the `table_id` referenced by `scope_id`.  |

Currently, the following values for `key` are specified:

| Name                           | Description                                                                                                                    | Notes                                                                                                       | Scope(s)              |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | --------------------- |
| `version`                      | DuckLake format version.                                                                                                       | `1.1` | Global                |
| `created_by`                   | Tool used to write the DuckLake.                                                                                               | `DuckDB` followed by its source id | Global                |
| `data_path`                    | Path to data files, e.g., `s3://mybucket/myprefix/`.                                                                           | Has to end in `/`                                                                                           | Global                |
| `encrypted`                    | Whether or not to encrypt Parquet files written to the data path.                                                              | `'true'` or `'false'`                                                                                       | Global                |
| `data_inlining_row_limit`      | Maximum amount of rows to inline in a single insert.                                                                           |                                                                                                             | Global, Schema, Table |
| `target_file_size`             | The target data file size for insertion and compaction operations.                                                             |                                                                                                             | Global, Schema, Table |
| `parquet_row_group_size_bytes` | Number of bytes per row group in Parquet files.                                                                                |                                                                                                             | Global, Schema, Table |
| `parquet_row_group_size`       | Number of rows per row group in Parquet files.                                                                                 |                                                                                                             | Global, Schema, Table |
| `parquet_compression`          | Compression algorithm for Parquet files, e.g., `zstd`.                                                                         | `uncompressed`, `snappy`, `gzip`, `zstd`, `brotli`, `lz4`, `lz4_raw`                                        | Global, Schema, Table |
| `parquet_compression_level`    | Compression level for Parquet files.                                                                                           |                                                                                                             | Global, Schema, Table |
| `parquet_version`              | Parquet format version.                                                                                                        | Stored as `V1` or `V2` (option values `1` or `2`)                                                                                                  | Global, Schema, Table |
| `hive_file_pattern`            | If partitioned data should be written in a Hive-style folder structure.                                                        | `'true'` or `'false'`                                                                                       | Global, Schema, Table |
| `require_commit_message`       | If an explicit commit message is required for a snapshot commit.                                                               | `'true'` or `'false'`                                                                                       | Global                |
| `rewrite_delete_threshold`     | Minimum amount of data (0-1) that must be removed from a file before a rewrite is warranted.                                   | Value between `0` and `1`                                                                                   | Global, Schema, Table |
| `delete_older_than`            | How old unused files must be to be removed by the `ducklake_delete_orphaned_files` and `ducklake_cleanup_old_files` functions. | Duration string (e.g., `7d`, `24h`)                                                                         | Global                |
| `expire_older_than`            | How old snapshots must be, by default, to be expired by `ducklake_expire_snapshots`.                                           | Duration string (e.g., `30d`)                                                                               | Global                |
| `auto_compact`                 | Whether compaction functions run on a table. Defaults to `true`.                                                               | Used by `ducklake_flush_inlined_data`, `ducklake_merge_adjacent_files`, `ducklake_rewrite_data_files`, etc. | Global, Schema, Table |
| `per_thread_output`            | Whether to create separate output files per thread during parallel insertion.                                                  | `'true'` or `'false'`                                                                                       | Global, Schema, Table |
| `write_deletion_vectors`       | Whether deletes are written as deletion vectors instead of Parquet delete files.                                               | `'true'` or `'false'`; experimental                                                                         | Global, Schema, Table |
| `sort_on_insert`               | Whether inserted data follows the table's sort order.                                                                          | `'true'` or `'false'`; defaults to `true`                                                                    | Global, Schema, Table |
| `skip_stats_columns`           | Columns for which min/max bounds are omitted from newly collected statistics.                                                   | Comma-separated column ids, e.g., `2,3`; an empty string clears the selection                                | Table                 |

`CREATE TABLE ... WITH (...)` and `ALTER TABLE ... SET (...)` write option rows with `scope = 'table'` and `scope_id` equal to the table's `table_id`. `ALTER TABLE ... RESET (...)` removes the corresponding rows. Option rows are not versioned by snapshots.

For example:

```sql
CREATE TABLE my_ducklake.my_table (id INTEGER, payload VARCHAR)
    WITH (skip_stats_columns = ['payload']);
ALTER TABLE my_ducklake.my_table SET (parquet_compression = 'zstd');
ALTER TABLE my_ducklake.my_table RESET (parquet_compression);
```

`skip_stats_columns` resolves column names to ids before storing the option. For the table above, `payload` has column id `2`, so the stored value is `2`. Schema-scoped options apply only to tables directly in that schema.

Snapshot expiration removes table- and schema-scoped options when the corresponding object is removed from the catalog.

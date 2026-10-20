---
layout: docu
title: ducklake_data_file
---

Data files contain the actual row data.

| Column name         | Column type |             |
| ------------------- | ----------- | ----------- |
| `data_file_id`      | `BIGINT`    | Primary key |
| `table_id`          | `BIGINT`    |             |
| `begin_snapshot`    | `BIGINT`    |             |
| `end_snapshot`      | `BIGINT`    |             |
| `file_order`        | `BIGINT`    |             |
| `path`              | `VARCHAR`   |             |
| `path_is_relative`  | `BOOLEAN`   |             |
| `file_format`       | `VARCHAR`   |             |
| `record_count`      | `BIGINT`    |             |
| `file_size_bytes`   | `BIGINT`    |             |
| `footer_size`       | `BIGINT`    |             |
| `row_id_start`      | `BIGINT`    |             |
| `partition_id`      | `BIGINT`    |             |
| `encryption_key`    | `VARCHAR`   |             |
| `mapping_id`        | `BIGINT`    |             |
| `partial_max`       | `BIGINT`    |             |
| `row_group_count`   | `BIGINT`    |             |

- `data_file_id` is the numeric identifier of the file. It is a primary key. `data_file_id` is incremented from `next_file_id` in the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}).
- `table_id` refers to a `table_id` from the [`ducklake_table` table]({% link docs/stable/specification/tables/ducklake_table.md %}).
- `begin_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The file is part of the table *starting with* this snapshot id.
- `end_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The file is part of the table *up to but not including* this snapshot id. If `end_snapshot` is `NULL`, the file is currently part of the table.
- `file_order` is a number that defines the vertical position of the file in the table. It is optional; DuckDB leaves this field `NULL`.
- `path` is the file path of the data file, e.g., `my_file.parquet` for a relative path.
- `path_is_relative` whether the `path` is relative to the [`path`]({% link docs/stable/specification/tables/ducklake_table.md %}) of the table (true) or an absolute path (false).
- `file_format` is the storage format of the file. Currently, only `parquet` is allowed.
- `record_count` is the number of records (row) in the file.
- `file_size_bytes` is the size of the file in bytes.
- `footer_size` is the size of the file metadata footer, in the case of Parquet the Thrift data. This is an optimization that allows for faster reading of the file.
- `row_id_start` is the first logical row id in the file. (Every row has a unique row id that is maintained.) If `row_id_start` is `NULL`, row ids are stored in the `_ducklake_internal_row_id` column in the Parquet file.
- `partition_id` refers to a `partition_id` from the `ducklake_partition_info` table.
- `encryption_key` contains the encryption for the file if [encryption]({% link docs/stable/duckdb/advanced_features/encryption.md %}) is enabled.
- `mapping_id` refers to a `mapping_id` from the [`ducklake_column_mapping` table]({% link docs/stable/specification/tables/ducklake_column_mapping.md %}).
- `partial_max` is the maximum snapshot id stored in a partial data file. When multiple snapshots are [merged into a single file]({% link docs/stable/duckdb/maintenance/merge_adjacent_files.md %}), per-row snapshot ownership is tracked via the `_ducklake_internal_snapshot_id` column embedded in the Parquet file. `partial_max` records the highest snapshot id present in that merged file, so reads and time travel can determine whether snapshot filtering is necessary. If it is `NULL`, all rows were inserted at `begin_snapshot`.
- `row_group_count` is the number of Parquet row groups in the file, or `NULL` if unknown.

---
layout: docu
title: ducklake_delete_file
---

Delete files contain the positions of rows that are deleted within a data file. Each data file can have its own delete file if any deletes are present for this data file.

| Column name        | Column type |             |
| ------------------ | ----------- | ----------- |
| `delete_file_id`   | `BIGINT`    | Primary key |
| `table_id`         | `BIGINT`    |             |
| `begin_snapshot`   | `BIGINT`    |             |
| `end_snapshot`     | `BIGINT`    |             |
| `data_file_id`     | `BIGINT`    |             |
| `path`             | `VARCHAR`   |             |
| `path_is_relative` | `BOOLEAN`   |             |
| `format`           | `VARCHAR`   |             |
| `delete_count`     | `BIGINT`    |             |
| `file_size_bytes`  | `BIGINT`    |             |
| `footer_size`      | `BIGINT`    |             |
| `encryption_key`   | `VARCHAR`   |             |
| `partial_max`      | `BIGINT`    |             |
| `row_group_count`  | `BIGINT`    |             |

- `delete_file_id` is the numeric identifier of the delete file. It is a primary key. `delete_file_id` is incremented from `next_file_id` in the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}).
- `table_id` refers to a `table_id` from the [`ducklake_table` table]({% link docs/stable/specification/tables/ducklake_table.md %}).
- `begin_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The delete file is part of the table *starting with* this snapshot id. For a partial delete file, this is the earliest deletion snapshot it contains.
- `end_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The delete file is part of the table *up to but not including* this snapshot id. If `end_snapshot` is `NULL`, the delete file is currently part of the table.
- `data_file_id` refers to a `data_file_id` from the `ducklake_data_file` table.
- `path` is the file name of the delete file, e.g., `my_file-deletes.parquet` for a relative path.
- `path_is_relative` whether the `path` is relative to the [`path`]({% link docs/stable/specification/tables/ducklake_table.md %}) of the table (true) or an absolute path (false).
- `format` is the storage format of the delete file. Supported values are `parquet` (positional delete file) and `puffin` (Iceberg V3 deletion vector, experimental).
- `delete_count` is the number of distinct deleted row positions at the latest snapshot represented in the file. For cumulative Puffin vectors, this is the latest vector's count, not the sum of the vectors.
- `file_size_bytes` is the size of the file in bytes.
- `footer_size` is the size of the file metadata footer, in the case of Parquet the Thrift data. This is an optimization that allows for faster reading of the file. For a Puffin container, it includes the JSON payload and the 16-byte footer structure. A bare deletion vector has no footer and stores `0`.
- `encryption_key` contains the encryption for the file if [encryption]({% link docs/stable/duckdb/advanced_features/encryption.md %}) is enabled. Puffin files are written without encryption, even if this field is populated.
- `partial_max` is the maximum snapshot id stored in a partial deletion file. When multiple deletes target the same data file across different snapshots, the deletion file is rewritten as a partial deletion file that tracks which rows were deleted in which snapshot. This column stores the highest snapshot id present in such a file. It is `NULL` for standard (non-partial) delete files.
- `row_group_count` is the number of Parquet row groups in the delete file, or `NULL` for Puffin files or when unknown.

DuckLake format version 1.1 supports Puffin files with cumulative deletion vectors for several snapshots. Each vector's `ducklake-snapshot-id` property identifies its snapshot; readers select the vector with the greatest snapshot id that does not exceed the requested snapshot. A file for a single deletion snapshot can contain a bare `deletion-vector-v1` blob, whose snapshot is given by `begin_snapshot`.

A replacement delete file preserves earlier deletions and their snapshot information. The old row is removed from `ducklake_delete_file`, and its file is added to [`ducklake_files_scheduled_for_deletion`]({% link docs/stable/specification/tables/ducklake_files_scheduled_for_deletion.md %}).

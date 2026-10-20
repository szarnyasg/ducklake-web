---
layout: docu
title: ducklake_snapshot_changes
---

This table lists changes that happened in a snapshot for easier conflict detection.

| Column name         | Column type |             |
| ------------------- | ----------- | ----------- |
| `snapshot_id`       | `BIGINT`    | Primary key |
| `changes_made`      | `VARCHAR`   |             |
| `author`            | `VARCHAR`   |             |
| `commit_message`    | `VARCHAR`   |             |
| `commit_extra_info` | `VARCHAR`   |             |

The `ducklake_snapshot_changes` table contains a summary of changes made by a snapshot. This table is used during [Conflict Resolution]({% link docs/stable/duckdb/advanced_features/conflict_resolution.md %}) to quickly find out if two snapshots have conflicting changesets.

- `snapshot_id` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}).
- `changes_made` is a comma-separated list of high-level changes made by the snapshot. The values that are contained in this list have the following format:
    - `created_schema:⟨schema_path⟩`{:.language-sql .highlight} – the snapshot created a schema with the given path.
    - `created_table:⟨schema_path⟩.⟨table_name⟩`{:.language-sql .highlight} – the snapshot created a table with the given name.
    - `created_view:⟨schema_path⟩.⟨view_name⟩`{:.language-sql .highlight} – the snapshot created a view with the given name.
    - `created_scalar_macro:⟨schema_path⟩.⟨macro_name⟩`{:.language-sql .highlight} – the snapshot created a scalar macro.
    - `created_table_macro:⟨schema_path⟩.⟨macro_name⟩`{:.language-sql .highlight} – the snapshot created a table macro.
    - `inserted_into_table:⟨table_id⟩`{:.language-sql .highlight} – the snapshot inserted data into the given table.
    - `deleted_from_table:⟨table_id⟩`{:.language-sql .highlight} – the snapshot deleted data from the given table.
    - `compacted_table:⟨table_id⟩`{:.language-sql .highlight} – the snapshot ran a compaction operation on the given table.
    - `merge_adjacent:⟨table_id⟩`{:.language-sql .highlight} – the snapshot merged adjacent files of the given table.
    - `rewrite_delete:⟨table_id⟩`{:.language-sql .highlight} – the snapshot rewrote files to remove deleted rows.
    - `inlined_insert:⟨table_id⟩`{:.language-sql .highlight} – the snapshot inserted inlined rows.
    - `inlined_delete:⟨table_id⟩`{:.language-sql .highlight} – the snapshot recorded inlined deletions.
    - `inline_flush:⟨table_id⟩`{:.language-sql .highlight} – the snapshot flushed inlined data.
    - `dropped_schema:⟨schema_id⟩`{:.language-sql .highlight} – the snapshot dropped the given schema.
    - `dropped_table:⟨table_id⟩`{:.language-sql .highlight} – the snapshot dropped the given table.
    - `dropped_view:⟨view_id⟩`{:.language-sql .highlight} – the snapshot dropped the given view.
    - `dropped_scalar_macro:⟨macro_id⟩`{:.language-sql .highlight} – the snapshot dropped a scalar macro.
    - `dropped_table_macro:⟨macro_id⟩`{:.language-sql .highlight} – the snapshot dropped a table macro.
    - `altered_table:⟨table_id⟩`{:.language-sql .highlight} – the snapshot altered the given table.
    - `altered_view:⟨view_id⟩`{:.language-sql .highlight} – the snapshot altered the given view.
- `author` is the author of the snapshot.
- `commit_message` is the commit message associated with the snapshot.
- `commit_extra_info` contains extra information regarding the commit.

> Names are written in quoted-format using SQL-style escapes, i.e., the name `this "table" contains quotes` is written as `"this ""table"" contains quotes"`.

Schema paths include all parent schema names, without the catalog name. For example, a table in a nested schema is recorded as `created_table:"sales"."europe"."orders"`.

Snapshot expiration keeps rows in `ducklake_snapshot_changes` after removing the corresponding rows from `ducklake_snapshot`.

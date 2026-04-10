---
layout: docu
title: ducklake_schema_versions
---

This table contains the schema versions for a range of snapshots. It is necessary to compact files with different schemas.

| Column name      | Column type |     |
| ---------------- | ----------- | --- |
| `begin_snapshot` | `BIGINT`    |     |
| `schema_version` | `BIGINT`    |     |
| `table_id`       | `BIGINT`    |     |

- `begin_snapshot` refers to a `snapshot_id` in the `ducklake_snapshot` table.
- `schema_version` refers to the `schema_version` of a `ducklake_snapshot`.
- `table_id` refers to the id of the table, allowing to track the schema changes per table.

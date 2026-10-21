---
layout: docu
title: ducklake_partition_info
---

| Column name      | Column type |             |
| ---------------- | ----------- | ----------- |
| `partition_id`   | `BIGINT`    |             |
| `table_id`       | `BIGINT`    |             |
| `begin_snapshot` | `BIGINT`    |             |
| `end_snapshot`   | `BIGINT`    |             |

- `partition_id` is a numeric identifier for a partitioning specification. `partition_id` is incremented from `next_catalog_id` in the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}).
- `table_id` refers to a `table_id` from the [`ducklake_table` table]({% link docs/stable/specification/tables/ducklake_table.md %}).
- `begin_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The partitioning specification is valid *starting with* this snapshot id.
- `end_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The partitioning specification is valid *up to but not including* this snapshot id. If `end_snapshot` is `NULL`, the partitioning specification is currently valid.

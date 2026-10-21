---
layout: docu
title: ducklake_view_column_tag
---

View columns can also have tags, which are defined in this table.
View column tags require DuckLake format version 1.1.

| Column name      | Column type |     |
| ---------------- | ----------- | --- |
| `view_id`        | `BIGINT`    |     |
| `column_name`    | `VARCHAR`   |     |
| `begin_snapshot` | `BIGINT`    |     |
| `end_snapshot`   | `BIGINT`    |     |
| `key`            | `VARCHAR`   |     |
| `value`          | `VARCHAR`   |     |

* `view_id` refers to a `view_id` from the [`ducklake_view` table]({% link docs/stable/specification/tables/ducklake_view.md %}).
* `column_name` is the name of the view column as produced by the view's query, before the view's `column_aliases` are applied. For example, for `CREATE VIEW v (x) AS SELECT id FROM t`, a comment on `x` is stored with `column_name` `id`. View columns are identified by name rather than by a `column_id`.
* `begin_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The tag is valid *starting with* this snapshot id.
* `end_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The tag is valid *up to but not including* this snapshot id. If `end_snapshot` is `NULL`, the tag is currently valid.
* `key` is the tag key and cannot be `NULL`. DuckDB stores SQL comments under the `comment` key.
* `value` is the tag value.

Replacing a tag ends the previous tag version and creates a new one. Dropping a view ends its column tags. Expiring snapshots removes tag versions that are no longer visible in any retained snapshot.

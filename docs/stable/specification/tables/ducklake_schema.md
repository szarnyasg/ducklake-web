---
layout: docu
title: ducklake_schema
---

This table defines valid schemas.

| Column name        | Column type |             |
| ------------------ | ----------- | ----------- |
| `schema_id`        | `BIGINT`    | Primary key |
| `schema_uuid`      | `UUID`      |             |
| `begin_snapshot`   | `BIGINT`    |             |
| `end_snapshot`     | `BIGINT`    |             |
| `schema_name`      | `VARCHAR`   |             |
| `path`             | `VARCHAR`   |             |
| `path_is_relative` | `BOOLEAN`   |             |
| `parent_schema_id` | `BIGINT`    |             |

- `schema_id` is the numeric identifier of the schema. `schema_id` is incremented from `next_catalog_id` in the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}).
- `schema_uuid` is a UUID that gives a persistent identifier for this schema. The UUID is stored here for compatibility with existing lakehouse formats.
- `begin_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The schema exists *starting with* this snapshot id.
- `end_snapshot` refers to a `snapshot_id` from the [`ducklake_snapshot` table]({% link docs/stable/specification/tables/ducklake_snapshot.md %}). The schema exists *up to but not including* this snapshot id. If `end_snapshot` is `NULL`, the schema is currently valid.
- `schema_name` is the name of the schema, e.g., `my_schema`. For a nested schema, only the final component of its name is stored.
- `path` is the `data_path` of the schema.
- `path_is_relative` whether the `path` is relative to the [`data_path`]({% link docs/stable/specification/tables/ducklake_metadata.md %}) of the catalog (true) or an absolute path (false).
- `parent_schema_id` refers to the `schema_id` of the parent schema in this table. It is `NULL` for a top-level schema.

Nested schemas require DuckLake format version 1.1. Their relative `path` is relative to the catalog's `data_path`, not their parent's path. DuckDB uses a directory named after the nested schema's UUID.

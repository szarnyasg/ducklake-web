---
layout: docu
title: Views
---

Views can be created using the standard [`CREATE VIEW` syntax](https://duckdb.org/docs/current/sql/statements/create_view).
The views are stored in the metadata, in the [`ducklake_view`]({% link docs/stable/specification/tables/ducklake_view.md %}) table.

## Examples

Create a view.

```sql
CREATE VIEW v1 AS SELECT * FROM tbl;
```

View columns support [`COMMENT ON COLUMN`]({% link docs/stable/duckdb/advanced_features/comments.md %}) with DuckLake format version 1.1.

References to the view's own DuckLake catalog are stored without the catalog name, allowing views to be queried after reattaching the catalog under a different alias.
When views reference [nested schemas]({% link docs/stable/duckdb/advanced_features/nested_schemas.md %}), keep parent schema names distinct from other attached catalog names to avoid ambiguous references in the stored SQL.

The `sql` column of `duckdb_views()` includes the view's schema in the `CREATE VIEW` statement when it is outside the `main` schema.

DuckLake does not support secure views.

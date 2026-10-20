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
The stored SQL omits the DuckLake catalog name, so keep schema names distinct from other attached catalog names.
Otherwise, a reference such as `sales.tbl` becomes ambiguous, and a reference into a [nested schema]({% link docs/stable/duckdb/advanced_features/nested_schemas.md %}) such as `sales.europe.orders` resolves to an attached catalog named `sales`.

The `sql` column of `duckdb_views()` includes the view's schema in the `CREATE VIEW` statement when it is outside the `main` schema.

DuckLake does not support secure views.

---
layout: docu
title: Views
---

Views can be created using the standard [`CREATE VIEW` syntax](https://duckdb.org/docs/stable/sql/statements/create_view).
The views are stored in the metadata, in the [`ducklake_view`]({% link docs/preview/specification/tables/ducklake_view.md %}) table.

## Examples

Create a view.

```sql
CREATE VIEW v1 AS SELECT * FROM tbl;
```

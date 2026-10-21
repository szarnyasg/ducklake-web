---
layout: docu
title: Row Lineage
---

Every row created in DuckLake has a row identifier that is unique within its table, which can be queried as the `rowid` virtual column.
The persistent identifier is assigned when the transaction inserting the row commits.
The identifier is preserved when the row is moved between files – for example as part of `UPDATE` and compaction operations.

The `rowid` column can be used to track whether the addition of files actually introduces new rows into DuckLake, or whether the operation is simply moving files around.
This is used internally in the [data change feed]({% link docs/stable/duckdb/advanced_features/data_change_feed.md %}) to differentiate between update operations and delete + insert operations.

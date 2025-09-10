---
layout: docu
title: Rewrite Heavily Deleted Files
---

DuckLake uses a merge-on-read strategy when data is deleted from a table. In short, this means that DuckLake uses a delete file which contains a pointer to the deleted records on the original file. This makes deletes very efficient. However, for heavily deleted tables, reading performance will be hindered by this approach. To solve this problem, DuckLake exposes a function called `ducklake_rewrite_data_files` that rewrites files that contain an amount of deletes bigger than a given threshold to a new file that contains non deleted records. This files can then be further compacted with a [`ducklake_merge_adjacent_files`]({% link docs/preview/duckdb/maintenance/merge_adjacent_files.md %}) operation. The default value for the delete threshold is 0.95.

## Usage

What follows are some examples on how to use the rewrite function.

```sql
-- Apply to all tables in a catalog
CALL ducklake_rewrite_data_files('my_ducklake');

-- Apply only to a specific table
CALL ducklake_rewrite_data_files('my_ducklake', 't');

-- Provide a specific value for the delete threshold
CALL ducklake_rewrite_data_files('my_ducklake', 't', delete_threshold => 0.5);

-- Set a specific threshold for the whole catalog
CALL ducklake_set_option('my_ducklake', 'rewrite_delete_threshold', 0.5);
```

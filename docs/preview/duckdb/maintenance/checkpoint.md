---
layout: docu
title: Checkpoint
---

DuckLake provides the option to implement all the maintenance functions bundled in the `CHECKPOINT` statement. This statement will run in order the following DuckLake functions:

- `ducklake_flush_inlined_data`
- `ducklake_expire_snapshots`
- `ducklake_merge_adjacent_files`
- `ducklake_rewrite_data_files`
- `ducklake_cleanup_old_files`
- `ducklake_delete_orphaned_files`

The `CHECKPOINT` statement takes the following global DuckLake options:

-`rewrite_delete_threshold`: A threshold that determines the minimum amount of data that must be removed from a file before a rewrite is warranted. From 0 to 1. Used by `ducklake_rewrite_data_files`.
- `delete_older_than`: How old unused files must be to be removed by the `ducklake_delete_orphaned_files` and `ducklake_cleanup_old_files` cleanup functions.
- `expire_older_than`: How old snapshots must be, by default, to be expired by `ducklake_expire_snapshots`.
- `compaction_schema`: Pre-defined schema used as a default value for the following compaction functions:
    - `ducklake_flush_inlined_data`
    - `ducklake_merge_adjacent_files`
    - `ducklake_rewrite_data_files`
    - `ducklake_delete_orphaned_files`
- `compaction_table`: Pre-defined table used as a default value for the following compaction functions:
    - `ducklake_flush_inlined_data`
    - `ducklake_merge_adjacent_files`
    - `ducklake_rewrite_data_files`
    - `ducklake_delete_orphaned_files`

If these options are not provided via the `ducklake.set_option` function, `CHECKPOINT` will use the default values when applicable and will run a `CHECKPOINT` of the whole DuckLake.

## Usage

```sql
CHECKPOINT;
```

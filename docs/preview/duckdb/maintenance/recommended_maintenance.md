---
layout: docu
title: Recommended Maintenance
---

## Metadata Maintenance

Most operations performed by DuckLake happen in the catalog database.
As such, the maintenance of the metadata server are handled by the chosen catalog database.
For example, when running PostgreSQL, it is likely sufficient to occasionally run `VACUUM` in order to ensure the system stays performant.

## Data File Maintenance

The data files that DuckLake writes to the data directory may require maintenance depending on how the insertions take place.
When snapshots write small batches of data at a time and [data inlining is not used]({% link docs/preview/duckdb/advanced_features/data_inlining.md %}) small Parquet files will be written to storage.
It is recommended to merge these Parquet files using the [`merge_adjacent_files`]({% link docs/preview/duckdb/maintenance/merge_adjacent_files.md %}) function.

DuckLake also never deletes old data files. As old data remains accessible through [time travel]({% link docs/preview/duckdb/usage/time_travel.md %}).
Even when a table is dropped, the data files associated with that table are not deleted.
In order to trigger a delete of these files, the snapshots that refer to that table must be [expired]({% link docs/preview/duckdb/maintenance/expire_snapshots.md %}) and files should be [cleaned up]({% link docs/preview/duckdb/maintenance/cleanup_of_files.md %}).

If you have tables that are heavily deleted, it can be the case that you have a lot of delete files that will slow read performance. In this case, we recommend you run a function to [rewrite the deleted files]({% link docs/preview/duckdb/maintenance/rewrite_data_files.md %}).

If you need to run all of this operations periodically, then we recommend you use the [`CHECKPOINT`]({% link docs/preview/duckdb/maintenance/checkpoint.md %}) statement.

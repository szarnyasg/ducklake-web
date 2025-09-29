---
layout: docu
title: Partitioning
---

DuckLake tables can be partitioned by a user-defined set of partition keys.
When a DuckLake table has partitioning keys defined, any new data is split up into separate data files along the partitioning keys.
During query planning, the partitioning keys are used to prune which files are scanned.

The partitioning keys defined on a table only affect new data written to the table.
Previously written data will be kept partitioned by the keys the table had when that data was written.
This allows the partition layout of a table to evolve over-time as needed.

The partitioning keys for a file are stored in DuckLake.
These keys do not need to be necessarily stored within the files, or in the paths to the files.

## Examples

> By default, DuckLake supports [Hive style partitioning](https://duckdb.org/docs/stable/data/partitioning/hive_partitioning). If you want to avoid this style of partitions, you can opt out via using `CALL my_ducklake.set_option('hive_file_pattern', false)`

Set the partitioning keys of a table, such that new data added to the table is partitioned by these keys.

To partition on a column, use:

```sql
ALTER TABLE tbl SET PARTITIONED BY (part_key);
```

You can also partition using functions. For example, to partition based on the year/month of a timestamp, use:

```sql
ALTER TABLE tbl SET PARTITIONED BY (year(ts), month(ts));
```

Remove the partitioning keys of a table, such that new data added to the table is no longer partitioned.

```sql
ALTER TABLE tbl RESET PARTITIONED BY;
```

DuckLake supports the following partition clauses:

<div class="monospace_table"></div>

| Transform | Expression |
|-----------|------------|
| identity  | col_name   |
| year      | year(ts)   |
| month     | month(ts)  |
| day       | day(ts)    |
| hour      | hour(ts)   |

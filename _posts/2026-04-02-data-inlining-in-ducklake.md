---
layout: post
title: "Data Inlining in DuckLake: Unlocking Streaming for Data Lakes"
author: "Pedro Holanda"
excerpt: "How DuckLake's data inlining feature solves the small file problem and unlocks streaming for data lakes."
tags: ["deep dive"]
---

When you stream data into a data lake, every insertion creates a tiny Parquet file and metadata files. A thousand inserts per second means a thousand of these little files accumulating, which causes performance to degrade. The damage is done; you are then forced to compact your files, schedule and babysit these maintenance operations to keep your data lake running, which in turn affects performance even more while the maintenance job executes. [DuckLake](https://ducklake.select/) flips the script: because it uses an actual DBMS as a catalog, DuckLake is able to inline updates directly in the catalog, effectively solving the small file issue.

> TODO [Gabor]: What is inlining? We should define it.

Small files are never created. No compaction jobs to schedule or babysit. Queries stay fast from the get-go.

|                          | Traditional Data Lakes | DuckLake with Inlining   |
|--------------------------|------------------------|--------------------------|
| **Small insert**         | Creates a Parquet file | Stored in the catalog    |
| **Small delete**         | Creates a deletion file| Stored in the catalog    |
| **Files after 1K inserts** | 1,000 Parquet files  | 0 files                  |
| **Compaction needed**    | Yes, periodically      | No, flush when ready     |
| **Query performance**    | Degrades with file count | Not affected by small writes |
| **Configuration**        | Tuning required        | Works out of the box     |

## What Is the Problem?

Data lakes allow users to avoid [having their data held hostage](https://duckdb.org/library/dont-hold-my-data-hostage/) by a DBMS storage model. They work by storing data in open formats (most commonly [Parquet](https://parquet.apache.org/)). Most data lakes, like [Iceberg](https://iceberg.apache.org/), [Hudi](https://hudi.apache.org/), and [Delta](https://delta.io/), also store their metadata (the bits of information that tell you which files you need to read for a certain query) in open formats such as JSON and Avro files. This means anyone can implement a system that reads and writes these formats, freeing users from being locked in to a single commercial solution.

However, storing data this way creates performance issues. Every small write creates a new data file and updates the metadata. This leads to a proliferation of tiny objects in storage. On the read side, queries now have to traverse an increasing number of metadata entries just to figure out what to scan. These are particularly painful problems for streaming workloads as they perform many small insertions over long periods of time.

The typical example of a streaming workload is sensor data that is updated at a constant interval. For a practical example consider the following script using [`pyiceberg`](https://py.iceberg.apache.org/):

```python
from pyiceberg.catalog import load_catalog
from datetime import datetime
import pyarrow as pa

catalog = load_catalog("default")
schema = pa.schema([
    ("sensor_id", pa.int32()),
    ("temperature", pa.float64()),
    ("ts", pa.timestamp("us")),
])
table = catalog.create_table("default.readings", schema=schema)

for i in range(100):
    batch = pa.table({
        "sensor_id": [1],
        "temperature": [21.5],
        "ts": [datetime.now()],
    })
    table.append(batch)
```
In Iceberg (and other traditional data lakes), each of these tiny insertions would create its own Parquet file, bloating both the data and metadata layers and having a drastic impact on query performance.


The way data lake systems have addressed this is by implementing periodic compaction jobs that merge small files into larger ones to reduce I/O costs. But these compaction routines don't solve the problem at write time, you still pay the cost of creating all those tiny files, and they don't help query performance until they actually run.


[DuckLake](https://ducklake.select/) takes a fundamentally different approach. Because the catalog is managed by a DBMS of the user's choice, DuckLake can store small updates, insertions, and deletions directly in the catalog instead of writing them out as files. Database systems already have decades of research into efficiently handling exactly these types of small reads and writes, making them a natural fit for this workload.

Take the same sensor workload from above and run it against DuckLake:

```python
import duckdb

con = duckdb.connect()
con.execute("LOAD ducklake")
con.execute("ATTACH 'ducklake:sqlite:sensors.ducklake' AS lake (DATA_PATH 'sensor_data/')")
con.execute("""
    CREATE TABLE lake.readings (
        sensor_id INTEGER, temperature DOUBLE, ts TIMESTAMP
    )
""")

for i in range(100):
    con.execute(f"INSERT INTO lake.readings VALUES (1, 21.5, now())")

# How many Parquet files were created?
print(con.execute("SELECT count(*) FROM glob('sensor_data/*.parquet')").fetchone())
# (0,) -- zero files, everything is inlined in the catalog
```

After 100 inserts: **zero Parquet files**. All data lives in the catalog, and queries work exactly as expected. With Iceberg, those same 100 inserts would have created 100 Parquet files and 100 metadata snapshots.

The figure below depicts the exact difference between Iceberg and DuckLake for our sensor workload. Iceberg ends up with 300 files (Avro and JSON) created for its metadata and 100 Parquet files for its data. In DuckLake, the data lives in the catalog, and after flushing, exactly one Parquet file is created containing all the data.

<img src="/images/blog/ducklake_iceberg_comparison.png" alt="Comparison of Iceberg vs DuckLake after 100 single-row inserts. Iceberg creates 100 Parquet files and 100 metadata snapshots. DuckLake stores all data inlined in the catalog with zero Parquet files, and after flushing consolidates everything into a single Parquet file." />

## Why This Matters

This is not just a storage optimization. It changes what is practical with a data lake:

- **No compaction jobs.**  Small writes never create small files, so there is nothing to compact.
- **Queries don't drastically slow down.** Traditional data lakes get slower as small files pile up; small files make performance degrade because of the numerous I/O calls to open and transform them for the execution layer.  With inlining, streaming writes don't affect query performance because there are no extra files to scan.
- **Lower storage costs.** Fewer file writes means fewer compaction runs, which means fewer object storage operations and lower S3/GCS bills.
- **Simpler architecture.** Your streaming pipeline writes directly to DuckLake. When you're ready, a single `CHECKPOINT` stores inlined data as Parquet files.
- **Zero configuration.** Inlining is on by default. Queries are transparent. You never need to know whether data is inlined or in files.

Starting with DuckLake 1.0 (to be released in April, together with [DuckDB v1.5.2](https://duckdb.org/release_calendar)), all insert, delete, and update statements can be inlined. This is also available today in DuckDB v1.5.1 by installing DuckLake from core_nightly:

```sql
FORCE INSTALL ducklake FROM core_nightly;
LOAD ducklake;
```

In the rest of this blog post, we will cover how inlining works under the hood and present a benchmark comparison of DuckLake with and without inlining for a high-contention streaming workload.

## How It Works

If you're curious about what happens under the hood, this section walks through the internals. If you just want to use it, you can skip straight to the [benchmark](#streaming-benchmark).

When you insert, delete, or update fewer rows than the inlining threshold (10 by default), DuckLake stores the change in the catalog database instead of writing a Parquet file. This means you can stream thousands of small writes without creating any files. The threshold can be changed at the global, schema, or table level:

```sql
-- Global: change the default for all tables
SET ducklake_default_data_inlining_row_limit = 50;

-- Per-table: override for a specific table
ALTER TABLE lake.readings SET (data_inlining_row_limit = 100);

-- Disable inlining entirely
SET ducklake_default_data_inlining_row_limit = 0;
```

In practice, this means you can stream data into DuckLake without worrying about file explosion. DuckLake manages the inlined data through insertion and deletion tables in the catalog, tracked by internal tables in the [spec](https://ducklake.select/docs/preview/specification/tables/ducklake_inlined_data_tables). At query time, DuckLake seamlessly combines inlined data with any existing Parquet files, so queries always return the right result regardless of where the data lives. Below we walk through how each operation works.

### Insertion
When an insert falls below the threshold, DuckLake does not create a Parquet file. Instead, it stores the rows directly in an inlined data table inside the catalog database. This table contains the original columns plus three metadata columns: 
1. `row_id` - the identifier of that row
2. `begin_snapshot` - the snapshot where the row was inserted
3. `end_snapshot` - the snapshot where the row was deleted, or `NULL` if it is still live

These snapshot columns let DuckLake maintain full [time-travel](https://ducklake.select/docs/stable/duckdb/advanced_features/time_travel) support even for inlined data.

Let's walk through a concrete example. First, we set up a DuckLake catalog and create a table:

```sql
ATTACH 'ducklake:sqlite:sensors.ducklake' AS lake (DATA_PATH 'sensor_data/');

CREATE TABLE lake.readings (
    sensor_id INTEGER,
    temperature DOUBLE,
    ts TIMESTAMP
);
```

Now we insert a few small batches, each below the default threshold of 10 rows:

```sql
INSERT INTO lake.readings VALUES (1, 21.5, '2025-03-27 10:00:00');
INSERT INTO lake.readings VALUES (2, 22.1, '2025-03-27 10:00:10');
INSERT INTO lake.readings VALUES (1, 21.8, '2025-03-27 10:00:20');
```

None of these inserts created a Parquet file. Instead, all three rows live in the catalog database in an inlined data table named `ducklake_inlined_data_{table_id}_{schema_version}`. If we peek inside the catalog:

```sql
ATTACH 'sensors.ducklake' AS catalog_db;
SELECT * FROM catalog_db.ducklake_inlined_data_1_1;
```

```text
┌────────┬────────────────┬──────────────┬───────────┬─────────────┬─────────────────────┐
│ row_id │ begin_snapshot │ end_snapshot │ sensor_id │ temperature │         ts          │
│ int64  │     int64      │    int64     │   int32   │   double    │      timestamp      │
├────────┼────────────────┼──────────────┼───────────┼─────────────┼─────────────────────┤
│      0 │              2 │         NULL │         1 │        21.5 │ 2025-03-27 10:00:00 │
│      1 │              3 │         NULL │         2 │        22.1 │ 2025-03-27 10:00:10 │
│      2 │              4 │         NULL │         1 │        21.8 │ 2025-03-27 10:00:20 │
└────────┴────────────────┴──────────────┴───────────┴─────────────┴─────────────────────┘
```

Each insert created a new snapshot, but no new files. The `end_snapshot` is `NULL` for all rows because none have been deleted yet. Note that `begin_snapshot` starts at 2 because the `CREATE TABLE` statement itself takes snapshot 1.

If a delete targets a row that is still inlined, DuckLake handles it in place by setting the `end_snapshot` column on that row. No deletion file is created. For example:

```sql
DELETE FROM lake.readings WHERE sensor_id = 2;
```

```text
┌────────┬────────────────┬──────────────┬───────────┬─────────────┬─────────────────────┐
│ row_id │ begin_snapshot │ end_snapshot │ sensor_id │ temperature │         ts          │
│ int64  │     int64      │    int64     │   int32   │   double    │      timestamp      │
├────────┼────────────────┼──────────────┼───────────┼─────────────┼─────────────────────┤
│      0 │              2 │         NULL │         1 │        21.5 │ 2025-03-27 10:00:00 │
│      1 │              3 │            5 │         2 │        22.1 │ 2025-03-27 10:00:10 │
│      2 │              4 │         NULL │         1 │        21.8 │ 2025-03-27 10:00:20 │
└────────┴────────────────┴──────────────┴───────────┴─────────────┴─────────────────────┘
```

Sensor 2's row now has `end_snapshot = 5`, meaning it was deleted in snapshot 5. A regular query will filter it out, but time-travel queries can still see it.


### Deletion

Deletion inlining covers a different case: deleting rows that already live in Parquet files. Instead of rewriting the Parquet file or creating a separate deletion file, DuckLake records the deletion in a per-table inlined deletion table inside the catalog. This table tracks which rows in which Parquet files have been deleted, along with the snapshot that caused the deletion.

For example, let's say we have a `data.parquet` file with some sensor readings that we want to [add to our table](https://ducklake.select/docs/stable/duckdb/metadata/adding_files):

```sql
CALL ducklake_add_data_files('lake', 'readings', 'data.parquet');
SELECT * FROM lake.readings;
```

```text
┌───────────┬─────────────┬─────────────────────┐
│ sensor_id │ temperature │         ts          │
│   int32   │   double    │      timestamp      │
├───────────┼─────────────┼─────────────────────┤
│         1 │        20.0 │ 2025-03-27 09:00:00 │
│         2 │        19.5 │ 2025-03-27 09:00:10 │
│         3 │        21.2 │ 2025-03-27 09:00:20 │
│         4 │        18.8 │ 2025-03-27 09:00:30 │
└───────────┴─────────────┴─────────────────────┘
```

Now if we delete one row from this file, DuckLake does not rewrite the Parquet file. Instead, it creates an inlined deletion table in the catalog named `ducklake_inlined_delete_{table_id}`:

```sql
DELETE FROM lake.readings WHERE sensor_id = 3;

SELECT * FROM catalog_db.ducklake_inlined_delete_0;
```

```text
┌─────────┬────────┬────────────────┐
│ file_id │ row_id │ begin_snapshot │
│  int64  │ int64  │     int64      │
├─────────┼────────┼────────────────┤
│       0 │      2 │              6 │
└─────────┴────────┴────────────────┘
```

The entry tells DuckLake that row 2 in file 0 was deleted in snapshot 6. At query time, DuckLake filters out this row from the Parquet file scan, so it never shows up in the result.

### Updates

Updates are simply a deletion followed by an insertion, so they follow the exact same steps described above and are fully supported.

### Flush

Inlined data can of course grow over time, so DuckLake also provides a [flushing operation](https://ducklake.select/docs/stable/duckdb/advanced_features/data_inlining) that materializes inlined rows into consolidated Parquet files. This is useful when performance requires it or for migration purposes.

```sql
-- Flush all inlined data in the catalog
CALL ducklake_flush_inlined_data('lake');

-- Flush a specific table only
CALL ducklake_flush_inlined_data('lake', table_name => 'readings');
```

Alternatively, flushing is also part of the [checkpoint routine](https://ducklake.select/docs/stable/duckdb/maintenance/checkpoint), which runs all maintenance operations (flush, snapshot expiration, file merging, and cleanup) in sequence:

```sql
CHECKPOINT lake;
```

## Streaming Benchmark

To see the impact of inlining in practice, we simulate an autonomous car streaming sensor data into a DuckLake table. The workload inserts 10,000 rows per second, broken into batches of 10 rows each (1,000 batches per second). After each simulated day (864 million rows), we run a summary query and a checkpoint. We repeat this for 30 days, totaling approximately 25.9 billion rows.

In order to make the benchmark more realistic, we execute it on an EC2 instance (describe it) with a PostgreSQL RDS instance as the catalog. We use PostgreSQL as the catalog to allow for multi-user usage, and EC2 with S3 storage to properly account for the network overhead of writing to remote object storage.

We run the benchmark twice: once with inlining enabled (threshold set to 20, so our 10-row batches get inlined) and once with inlining disabled (threshold set to 0, so every batch writes a Parquet file).

[Write up about the benchmark when we execute it.]

## Conclusion

The small file problem has been one of the main pain points of data lakes for streaming workloads. Traditional systems create it at write time and clean it up afterwards in a maintenance job. DuckLake avoids it entirely by storing small changes directly in the catalog, where database systems have been optimizing exactly this kind of workload for decades.

Inlining works out of the box with zero configuration. Inserts, deletes, and updates are all supported. When the data is ready to be stored as Parquet files, a single checkpoint takes care of it.

Data inlining will ship with [DuckLake 1.0](https://ducklake.select/) in April alongside [DuckDB v1.5.2](https://duckdb.org/release_calendar), but you don't have to wait. Install DuckLake from core_nightly on DuckDB v1.5.1, point it at a streaming workload, and see the difference for yourself, run your own benchmarks, and get a feel for it. It takes five minutes to set up and zero configuration to run.

If you hit any issues, open them on [GitHub](https://github.com/duckdb/ducklake/issues). If you run into special cases and want to discuss them, we have an active community on the [DuckDB Discord](https://discord.duckdb.org/).

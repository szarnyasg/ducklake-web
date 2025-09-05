---
layout: docu
title: Backup and Recovery
---
DuckLake has two components: catalog and storage. The catalog contains all of DuckLake's metadata, while the storage contains all of the data files in Parquet format. The catalog is a [database]({% link docs/preview/duckdb/usage/choosing_a_catalog_database.md %}), while the storage layer can be any [filesystem backend supported by DuckDB]({% link docs/preview/duckdb/usage/choosing_storage.md %}). These two components have different backup strategies, so this document will address them separately.

> In this document, we will focus on disasters caused by human errors or application failures/malfunctions that result in data corruption or loss.

## Catalog Backup and Recovery

Backup and recovery strategies depend on the SQL database you are using as a DuckLake catalog.

### DuckDB Catalog

For DuckDB, the best approach is to perform regular backups of the metadata database. If the original database is corrupted, tampered with, or even deleted, you can recover from this backup.

```sql
-- Backup
ATTACH 'main.db' AS main (READ_ONLY);
ATTACH 'backup.db' AS backup;
COPY DATABASE FROM main TO backup;

-- Recover
ATTACH 'main.db' AS main;
ATTACH 'backup.db' AS backup (READ_ONLY);
COPY DATABASE FROM backup TO main;
ATTACH 'ducklake:main.db' AS my_ducklake;
```

It is very important to note that transactions committed to DuckLake after the metadata backup will not be tracked when recovering. The data from the transactions will exist in the data files, but the backup will point to a previous snapshot. If you are running batch jobs, make sure to always back up after the batch job. If you are regularly micro-batching or streaming data, then schedule periodic jobs to back up your metadata.

### SQLite Catalog

For SQLite, the process is exactly the same as with DuckDB and has the same implications.

```sql
-- Backup
ATTACH 'sqlite:main.db' AS main (READ_ONLY);
ATTACH 'sqlite:backup.db' AS backup;
COPY DATABASE FROM main TO backup;

-- Recover
ATTACH 'sqlite:main.db' AS main;
ATTACH 'sqlite:backup.db' AS backup (READ_ONLY);
COPY DATABASE FROM backup TO main;
ATTACH 'ducklake:sqlite:main.db' AS my_ducklake;
```

### PostgreSQL Catalog

For PostgreSQL, there are two main approaches to backup and recovery:

- [SQL dump](https://www.postgresql.org/docs/current/backup-dump.html): This approach is similar to the one mentioned for SQLite and DuckDB. This process can happen periodically and can only recover to a particular point in time (i.e., the time of the dump). For DuckLake, this will be a specific snapshot, and transactions after this snapshot will not be recorded.
- [Continuous Archiving and Point-in-Time Recovery (PITR)](https://www.postgresql.org/docs/current/continuous-archiving.html): This is a more complex approach but allows recovery to a specific point in time. For DuckLake, this means you can recover to a specific snapshot without losing any transactions.

Nothe that the SQL dump approach can also be managed by DuckDB using the [Postgres extension](https://duckdb.org/docs/stable/core_extensions/postgres). In fact, the backup can be a DuckDB file.

```sql
-- Backup
ATTACH 'postgres:connection_string' AS main (READ_ONLY);
ATTACH 'duckdb:backup.db' AS backup;
COPY DATABASE FROM main TO backup;

-- Recover
ATTACH 'postgres:connection_string' AS main;
ATTACH 'duckdb:backup.db' AS backup (READ_ONLY);
COPY DATABASE FROM backup TO main;
ATTACH 'ducklake:postgres:connection_string' AS my_ducklake;
```

> Cloud-hosted PostgreSQL solutions may offer different mechanisms. We encourage you to check what your specific vendor recommends as a strategy for backup and recovery.

## Storage Backup and Recovery

Backup and recovery of the data files also depend on the storage you are using. In this document, we will only focus on cloud-based object storage since it is the most common for Lakehouse architectures.

### S3

In S3, there are three main mechanisms that AWS offers to back up and/or restore data:

- [Cross-bucket replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [S3 backup service](https://docs.aws.amazon.com/aws-backup/latest/devguide/s3-backups.html)
- [Enable S3 versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)

Both the S3 backup service and S3 object versioning will restore data files in the same bucket. On the other hand, cross-bucket replication will copy the files to a different bucket, and therefore your DuckLake initialization should change:

```sql
-- Before
ATTACH 'ducklake:some.db' AS my_ducklake (DATA_PATH 's3://og-bucket/')

-- After
ATTACH 'ducklake:some.db' AS my_ducklake (DATA_PATH 's3://replication-bucket/')
```

### GCS

GCS has similar mechanisms to back up and/or restore data:

- [Cross-bucket replication](https://cloud.google.com/storage/docs/using-cross-bucket-replication)
- [Backup and DR service](https://cloud.google.com/backup-disaster-recovery/docs/concepts/backup-dr)
- [Object versioning](https://cloud.google.com/storage/docs/object-versioning) with soft deletes enabled

Regarding cross-bucket replication, repointing to the new bucket will be necessary.

```sql
-- Before
ATTACH 'ducklake:some.db' AS my_ducklake (DATA_PATH 'gs://og-bucket/')

-- After
ATTACH 'ducklake:some.db' AS my_ducklake (DATA_PATH 'gs://replication-bucket/')
```

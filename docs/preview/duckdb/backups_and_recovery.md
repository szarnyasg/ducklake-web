---
layout: docu
title: Backups and Recovery
---

DuckLake has two components: catalog and storage. The catalog contains all of DuckLake's metadata while the storage contains all of the data files in parquet format. The catalog is a [database]({% link docs/preview/duckdb/usage/choosing_a_catalog_database.md %}), while the storage layer can be any [filesystem backend supported by DuckDB]({% link docs/preview/duckdb/usage/choosing_storage.md %}). These two components have different backup strategies, and so this document will address them separately.

## Catalog Backup and Recovery

Backup and recovery strategies will depend on the SQL database that you are using as a DuckLake catalog.

### DuckDB Catalog

### SQLite Catalog

### PostgreSQL Catalog

## Storage Backup and Recovery

Backup and recovery of the data files also depends on the storage you are using. In this document we will only focus on cloud-based object storage since they are the most common for Lakehouse architectures.

### S3

### GCS
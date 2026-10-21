---
layout: docu
title: List Files
---

The `ducklake_list_files` function can be used to list the data files and corresponding delete files that belong to a given table, optionally for a given snapshot.

## Usage

List all files:

```sql
FROM ducklake_list_files('catalog', 'table_name');
```

Get list of files at a specific snapshot version:

```sql
FROM ducklake_list_files('catalog', 'table_name', snapshot_version => 2);
```

Get list of files at a specific point in time:

```sql
FROM ducklake_list_files('catalog', 'table_name', snapshot_time => '2025-06-16 15:24:30');
```

Get list of files of a table in a specific schema:

```sql
FROM ducklake_list_files('catalog', 'table_name', schema => 'main');
```

| Parameter          | Description                                      | Default |
| ------------------ | ------------------------------------------------ | ------- |
| `catalog`          | Name of attached DuckLake catalog                |         |
| `table_name`       | Name of table to fetch files from                |         |
| `schema`           | Schema for the table                             | Default schema |
| `snapshot_version` | If provided, fetch files for a given snapshot id |         |
| `snapshot_time`    | If provided, fetch files for a given timestamp   |         |

The `schema` argument also accepts nested paths such as `'some_schema.child'`.

## Result

The function returns the following result set.

<div class="monospace_table"></div>

| column_name                | column_type |
| -------------------------- | ----------- |
| data_file                  | VARCHAR     |
| data_file_size_bytes       | UBIGINT     |
| data_file_footer_size      | UBIGINT     |
| data_file_encryption_key   | BLOB        |
| delete_file                | VARCHAR     |
| delete_file_size_bytes     | UBIGINT     |
| delete_file_footer_size    | UBIGINT     |
| delete_file_encryption_key | BLOB        |

* If the file has delete files, the corresponding delete file is returned, otherwise these fields are `NULL`.
* If the database is encrypted, Parquet data and delete files must be read with the returned encryption key. Puffin deletion-vector files are written unencrypted, even though `delete_file_encryption_key` is also set for them.
* The `footer_size` refers to the Parquet or Puffin footer size. This is optionally provided, and is `0` for bare deletion-vector files.
* Delete files can be Parquet files or Puffin deletion-vector files.

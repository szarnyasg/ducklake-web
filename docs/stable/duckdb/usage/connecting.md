---
layout: docu
title: Connecting
---

To use DuckLake, you must first either connect to an existing DuckLake, or create a new DuckLake.
The `ATTACH` command can be used to select the DuckLake instance to connect to.
In the `ATTACH` command, you must specify the [catalog database]({% link docs/stable/duckdb/usage/choosing_a_catalog_database.md %}) and the [data storage location]({% link docs/stable/duckdb/usage/choosing_storage.md %}).
When attaching, a new DuckLake is automatically created if none exists in the specified catalog database.

Note that the data storage location only has to be specified when creating a new DuckLake.
When connecting to an existing DuckLake, the data storage location is loaded from the catalog database.

```sql
ATTACH 'ducklake:⟨metadata_storage_location⟩' (DATA_PATH '⟨data_storage_location⟩');
```

In addition, DuckLake connection parameters can also be stored in [secrets](https://duckdb.org/docs/stable/configuration/secrets_manager).

```sql
ATTACH 'ducklake:⟨secret_name⟩';
```

## Examples

Connect to DuckLake, reading the configuration from the default (unnamed) secret:

```sql
ATTACH 'ducklake:';
```

Connect to DuckLake, reading the configuration from the secret named `my_secret`:

```sql
ATTACH 'ducklake:my_secret';
```

Use a DuckDB database `duckdb_database.ducklake` as the catalog database with the data path defaulting to `duckdb_database.ducklake.files`:

```sql
ATTACH 'ducklake:duckdb_database.ducklake';
```

Use a DuckDB database `duckdb_database.ducklake` as the catalog database with the data path explicitly specified as the `my_files` directory:

```sql
ATTACH 'ducklake:duckdb_database.ducklake' (DATA_PATH 'my_files/');
```

Use a PostgreSQL database as the catalog database and an S3 path as the data path:

```sql
ATTACH 'ducklake:postgres:dbname=postgres' (DATA_PATH 's3://my-bucket/my-data/');
```

Connect to DuckLake in read-only mode:

```sql
ATTACH 'ducklake:postgres:dbname=postgres' (READ_ONLY);
```

It is also possible to override the data path for a particular connection. This will not change the value of the `data_path` stored in the DuckLake metadata, but it will override it for the current connection allowing data to be stored in a different path.

```sql
ATTACH 'ducklake:duckdb_database.ducklake' (DATA_PATH 'other_data_path/', OVERRIDE_DATA_PATH true);
```

> If `OVERRIDE_DATA_PATH` is used, data under the original `DATA_PATH` will not be able to be queried in the current connection. This behavior may be changed in the future to allow to query data in a catalog regardless of the current write `DATA_PATH`.

## Parameters

The following parameters are supported for `ATTACH`:

| Name                                               | Description                                                                                                             | Default                                                                                 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `CREATE_IF_NOT_EXISTS`                             | Creates a new DuckLake if the specified one does not already exist                                                      | `true`                                                                                  |
| `DATA_INLINING_ROW_LIMIT`                          | The number of rows for which [data inlining]({% link docs/stable/duckdb/advanced_features/data_inlining.md %}) is used  | `0`                                                                                     |
| `DATA_PATH`                                        | The storage location of the data files                                                                                  | `⟨metadata_file⟩.files`{:.language-sql .highlight} for DuckDB files, required otherwise |
| `ENCRYPTED`                                        | Whether or not data is stored encrypted                                                                                 | `false`                                                                                 |
| `META_⟨PARAMETER_NAME⟩`{:.language-sql .highlight} | Pass `⟨PARAMETER_NAME⟩`{:.language-sql .highlight} to the catalog server                                                |                                                                                         |
| `METADATA_CATALOG`                                 | The name of the attached catalog database                                                                               | `__ducklake_metadata_⟨ducklake_name⟩`{:.language-sql .highlight}                        |
| `METADATA_PARAMETERS`                              | Map of parameters to pass to the catalog server                                                                         | `{}`                                                                                    |
| `METADATA_PATH`                                    | The connection string for connecting to the metadata catalog                                                            |                                                                                         |
| `METADATA_SCHEMA`                                  | The schema in the catalog server in which to store the DuckLake tables                                                  | `main`                                                                                  |
| `MIGRATE_IF_REQUIRED`                              | Migrates the DuckLake schema if required                                                                                | `true`                                                                                  |
| `OVERRIDE_DATA_PATH`                               | If the path provided in `data_path` differs from the stored path and this option is set to true, the path is overridden | `true`                                                                                  |
| `SNAPSHOT_TIME`                                    | If provided, connect to DuckLake at a snapshot at a specified point in time                                             |                                                                                         |
| `SNAPSHOT_VERSION`                                 | If provided, connect to DuckLake at a specified snapshot id                                                             |                                                                                         |

In addition, any parameters that are prefixed with `META_` are passed to the catalog used to store the metadata.
The supported parameters depend on the metadata catalog that is used.
For example, `postgres` supports the `SECRET` parameter. By using the `META_SECRET` parameter we can pass this parameter to the PostgreSQL instance.

### Secrets

Instead of configuring the connection using `ATTACH`, secrets can be created that contain all required information for setting up a connection.
Secrets support the same list of parameters as `ATTACH`, in addition to the `METADATA_PATH` and `METADATA_PARAMETERS` parameters.

| Name                  | Description                                          | Default |
| --------------------- | ---------------------------------------------------- | ------- |
| `METADATA_PATH`       | The connection string for connecting to the metadata |         |
| `METADATA_PARAMETERS` | Map of parameters to pass to the catalog server      | `{}`    |

```sql
-- default (unnamed) secret
CREATE SECRET (
    TYPE ducklake,
    METADATA_PATH '⟨metadata.db⟩',
    DATA_PATH '⟨metadata_files/⟩'
);

ATTACH 'ducklake:' AS my_ducklake;

-- named secrets
CREATE SECRET ⟨my_secret⟩ (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://⟨my-s3-bucket⟩/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'postgres_secret'}
);
ATTACH 'ducklake:⟨my_secret⟩' AS my_ducklake;
```

To persist secrets, use the [`CREATE PERSISTENT SECRET` statement](https://duckdb.org/docs/stable/configuration/secrets_manager#persistent-secrets).

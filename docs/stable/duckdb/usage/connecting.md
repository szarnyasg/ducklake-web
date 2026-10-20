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

In addition, DuckLake connection parameters can also be stored in [secrets](https://duckdb.org/docs/current/configuration/secrets_manager).

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
ATTACH 'ducklake:⟨my_secret⟩';
```

Use a DuckDB database `duckdb_database.ducklake` as the catalog database with the data path defaulting to `duckdb_database.ducklake.files`:

```sql
ATTACH 'ducklake:⟨duckdb_database.ducklake⟩';
```

Use a DuckDB database `duckdb_database.ducklake` as the catalog database with the data path explicitly specified as the `my_files` directory:

```sql
ATTACH 'ducklake:⟨duckdb_database.ducklake⟩' (DATA_PATH '⟨my_files/⟩');
```

Use a PostgreSQL database as the catalog database and an S3 path as the data path:

```sql
ATTACH 'ducklake:postgres:dbname=postgres' (DATA_PATH 's3://⟨my-bucket/my-data/⟩');
```

Connect to DuckLake in read-only mode:

```sql
ATTACH 'ducklake:postgres:dbname=postgres' (READ_ONLY);
```

Use a SQLite metadata file with the `sqlite:` prefix:

```sql
ATTACH 'ducklake:sqlite:metadata.sqlite' AS my_ducklake (DATA_PATH 'my_files/');
```

Do not rely on an unprefixed SQLite file being detected automatically.

Use a [Quack server]({% link docs/stable/duckdb/usage/choosing_a_catalog_database.md %}#quack) as the catalog database:

```sql
CREATE SECRET (TYPE quack, TOKEN '⟨token⟩', SCOPE 'quack:localhost');
ATTACH 'ducklake:quack:localhost' AS my_ducklake (DATA_PATH 'my_files/');
```

It is also possible to override the data path for a particular connection. This will not change the value of the `DATA_PATH` stored in the DuckLake metadata, but it will override it for the current connection allowing data to be stored in a different path.

```sql
ATTACH 'ducklake:⟨duckdb_database.ducklake⟩' (DATA_PATH '⟨other_data_path/⟩', OVERRIDE_DATA_PATH true);
```

> If `OVERRIDE_DATA_PATH` is used, data under the original `DATA_PATH` will not be able to be queried in the current connection. This behavior may be changed in the future to allow to query data in a catalog regardless of the current write `DATA_PATH`.

New catalogs use version 1.1 by default. Existing 1.0 catalogs remain at 1.0 unless migration is requested:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake (AUTOMATIC_MIGRATION true);
```

Use `DUCKLAKE_VERSION '1.0'` to create a catalog at version 1.0.
See [“Upgrading to DuckLake 1.1”]({% link docs/stable/duckdb/migrations/upgrading_to_ducklake_1_1.md %}) for details.

## Parameters

The following parameters are supported for `ATTACH`:

| Name                                               | Description                                                                                                             | Default                                                                                 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `CREATE_IF_NOT_EXISTS`                             | Creates a new DuckLake if the specified one does not already exist                                                      | `true` (`false` with `READ_ONLY`)                                                                                 |
| `DATA_INLINING_ROW_LIMIT`                          | The number of rows for which [data inlining]({% link docs/stable/duckdb/advanced_features/data_inlining.md %}) is used  | `ducklake_default_data_inlining_row_limit` (`10`)                                                                                     |
| `DATA_PATH`                                        | The storage location of the data files                                                                                  | `⟨metadata_file⟩.files`{:.language-sql .highlight} for DuckDB files, required otherwise |
| `DUCKLAKE_VERSION`                                 | Requested catalog version: `'1.0'` or `'1.1'` (migration also requires `AUTOMATIC_MIGRATION`)                            | `ducklake_default_version`                                                             |
| `ENCRYPTED`                                        | Whether or not data is stored encrypted                                                                                 | `false`                                                                                 |
| `META_⟨PARAMETER_NAME⟩`{:.language-sql .highlight} | Pass `⟨PARAMETER_NAME⟩`{:.language-sql .highlight} to the catalog server                                                |                                                                                         |
| `METADATA_CATALOG`                                 | The name of the attached catalog database                                                                               | `__ducklake_metadata_⟨ducklake_name⟩`{:.language-sql .highlight}                        |
| `METADATA_PARAMETERS`                              | Map of parameters to pass to the catalog server                                                                         | `{}`                                                                                    |
| `METADATA_PATH`                                    | The connection string for connecting to the metadata catalog                                                            |                                                                                         |
| `METADATA_SCHEMA`                                  | The schema in the catalog server in which to store the DuckLake tables                                                  | Backend default (`main` for DuckDB/SQLite, usually `public` for PostgreSQL)                                                                                  |
| `AUTOMATIC_MIGRATION`                              | Migrates to the requested catalog version, or to 1.1 if no version is requested                                        | `false`                                                                                 |
| `OVERRIDE_DATA_PATH`                               | If the path provided in `data_path` differs from the stored path and this option is set to true, the path is overridden | `false`                                                                                  |
| `SNAPSHOT_TIME`                                    | If provided, connect to DuckLake at a snapshot at a specified point in time                                             |                                                                                         |
| `SNAPSHOT_VERSION`                                 | If provided, connect to DuckLake at a specified snapshot id                                                             |                                                                                         |

The metadata database is hidden from catalog listings unless `METADATA_CATALOG` is explicitly set.

In addition, any parameters that are prefixed with `META_` are passed to the catalog used to store the metadata.
The supported parameters depend on the metadata catalog that is used.
For example, `postgres` supports the `SECRET` parameter. By using the `META_SECRET` parameter we can pass this parameter to the PostgreSQL instance.

For PostgreSQL, an explicit `METADATA_SCHEMA` also scopes the underlying attachment to that schema.
An explicit `META_SCHEMA`, or a `schema` entry in `METADATA_PARAMETERS`, takes precedence for the underlying attachment.

### Secrets

Instead of configuring the connection using `ATTACH`, secrets can be created that contain all required information for setting up a connection.
Secrets support the following parameters. Other options, such as `READ_ONLY` and `AUTOMATIC_MIGRATION`, must be specified on `ATTACH`.
`METADATA_PATH` is required, even when the connection is configured through `METADATA_PARAMETERS`.

| Name                  | Description                                          | Default |
| --------------------- | ---------------------------------------------------- | ------- |
| `DATA_PATH`           | The storage location of the data files               |         |
| `DUCKLAKE_VERSION`    | Requested catalog version, `'1.0'` or `'1.1'`         |         |
| `ENCRYPTED`           | Whether or not data is stored encrypted              |         |
| `METADATA_CATALOG`    | Name of the attached metadata database               |         |
| `METADATA_SCHEMA`     | Schema containing the metadata tables                |         |
| `METADATA_PATH`       | The connection string for connecting to the metadata |         |
| `METADATA_PARAMETERS` | Map of parameters to pass to the catalog server      | `{}`    |

```sql
-- Default (unnamed) secret
CREATE SECRET (
    TYPE ducklake,
    METADATA_PATH '⟨metadata.duckdb⟩',
    DATA_PATH '⟨metadata_files/⟩'
);

ATTACH 'ducklake:' AS my_ducklake;

-- Named secrets
CREATE SECRET ⟨my_secret⟩ (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://⟨my-s3-bucket⟩/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'postgres_secret'}
);
ATTACH 'ducklake:⟨my_secret⟩' AS my_ducklake;
```

To persist secrets, use the [`CREATE PERSISTENT SECRET` statement](https://duckdb.org/docs/current/configuration/secrets_manager#persistent-secrets).

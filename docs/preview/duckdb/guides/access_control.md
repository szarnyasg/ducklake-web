---
layout: docu
title: Access Control
---

While access control is not perse a feature of DuckLake, you can laverage the tools that DuckLake uses and their permission systems to implement schema and table level permissions in DuckLake.

## Basic principles

In this guide we are going to focus on three different roles regarding Access Control in DuckLake. These are:

- **DuckLake Superuser**. The DuckLake Superuser can do any DuckLake operation, most notably:
    - Initializing DuckLake. This is done the first time you run the `ATTACH` command.
    - Create schemas.
    - `CREATE, INSERT, UPDATE, DELETE, SELECT` on any DuckLake table.

- **DuckLake Writer**. The DuckLake Writer can do the following operations:
    - `ATTACH` to an existing DuckLake
    - `CREATE, INSERT, UPDATE, DELETE, SELECT` on any or a subset of DuckLake tables.
    - Optionally `SELECT` on any or a subset of DuckLake tables.
    - Optionally `CREATE` schema.

- **DuckLake Reader**: The DuckLake Reader can do the following operations:
    - `ATTACH` to an existing DuckLake. Note that both `READ_ONLY` and regular attaching modes will work.
    - `SELECT` on any or a subset of DuckLake tables.

> This roles are not really implemented in DuckLake; they are just constructs we are using in this guide since these are the most common types of roles that are present in data management systems.

There are two components in DuckLake: the metadata catalog, which lives in a SQL database and the storage, which can be any filesystem backend. The roles mentioned above would need different specific permissions at the **catalog level**:
- The DuckLake Superuser would need every permission under the specified schema (`public` by default). Since this user will initialize all of the tables, it will also become the owner. That means that subsequent migrations between DuckLake specs will need to be carried over by this user.
- The DuckLake Writer would only need permissions to select `INSERT, UPDATE, DELETE, SELECT` at the catalog level. This would be enough for any operation in DuckLake, including operations that expire snapshots.
- The DuckLake Reader only needs `SELECT` permissions at the catalog level.

At the storage level, we can laverage the way DuckLake structures data paths for different tables, which uses the following convention:

```
/<schema>/<table>/<partition>/<data_file>.parquet
```

Using this convention and the policy mechanisms of certain filesystems (like cloud-based object storage), we can establish access to certain paths at the schema, table or even partition level.

> Note that this will not work if you use the `ducklake_add_data_files` and the added files do not follow the path convention, then permissions at the path level will not apply to these files.

## Access Control with S3 and PostgreSQL

The following is an example implementation of the basic principles exposed above, focusing on PostgreSQL as a DuckLake catalog and S3 as the storage backend.

### PostgreSQL Requirements

In this section, we will create the three roles described above in PostgreSQL. We will create them as users for simplicity, but you may also create them as groups if you foresee that a specific role will be used by various users.

```sql
-- Setup initialization user, migrations and writing, assuming the database is created already
CREATE USER ducklake_superuser WITH PASSWORD 'simple';
GRANT CREATE ON DATABASE access_control TO ducklake_superuser;
GRANT CREATE, USAGE ON SCHEMA public TO ducklake_superuser;
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ducklake_superuser;

-- Only writer/reader
CREATE USER ducklake_writer WITH PASSWORD 'simple';
GRANT USAGE ON SCHEMA public TO ducklake_writer;
GRANT USAGE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ducklake_writer;

-- Only reader
CREATE USER ducklake_reader WITH PASSWORD 'simple';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ducklake_reader;
```

### S3 Requirements

In AWS we are going to create three users. The writer user will only have access to a specific schema and the reader will only have access to a specific table. The policies needed for this users are the following:

**DuckLake Superuser**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DucklakeSuperuser",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::ducklake-access-control",
        "arn:aws:s3:::ducklake-access-control/*"
      ]
    }
  ]
}
```

**DuckLake Writer/Reader**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DucklakeWriter",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::ducklake-access-control",
        "arn:aws:s3:::ducklake-access-control/some_schema/*"
      ]
    }
  ]
}
```

Note that we are allowing `s3:DeleteObject` which will enable the writer to do compaction and cleanup jobs, which require rewriting data files.

**DuckLake Reader**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DucklakeReader",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
      ],
      "Resource": [
        "arn:aws:s3:::ducklake-access-control",
        "arn:aws:s3:::ducklake-access-control/some_schema/some_table/*"
      ]
    }
  ]
}
```

### DuckLake Test

In this section we will connect to DuckLake using this different roles to showcase how the implementation would work in practice using the DuckLake extension of DuckDB.

Let's initialize the DuckLake and do some basic operations with the **DuckLake Superuser**.

```sql
-- Using the credentials for the AWS DuckLake Superuser (note that other providers such as STS or SSO can be used too)
CREATE OR REPLACE SECRET s3_ducklake_superuser (
    TYPE s3,
    PROVIDER config,
    KEY_ID '<key>',
    SECRET '<secret>',
    REGION 'eu-north-1'
);

-- Using the DuckLake Superuser credentials for postgres
CREATE OR REPLACE SECRET postgres_secret_superuser (
    TYPE postgres,
    HOST 'localhost',
    DATABASE 'access_control',
    USER 'ducklake_superuser',
    PASSWORD 'simple'
);

-- DuckLake config secret
CREATE OR REPLACE SECRET ducklake_superuser_secret (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://ducklake-access-control/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres','SECRET': 'postgres_secret_superuser'}
);

-- This will initialize DuckLake
ATTACH 'ducklake:ducklake_superuser_secret' as ducklake_superuser;
USE ducklake_superuser;

-- Do some stuff in DuckLake
CREATE SCHEMA IF NOT EXISTS some_schema;
CREATE TABLE IF NOT EXISTS some_schema.some_table (id INTEGER, name VARCHAR);
INSERT INTO some_schema.some_table VALUES (1, 'test')
```

Now let's put on the hat of the **DuckLake Writer**:

```sql
-- Drop this to avoid the extension to default to this secret
DROP SECRET s3_ducklake_superuser;

-- Using the DuckLake Writer credentials for postgres
CREATE OR REPLACE SECRET postgres_secret_writer (
    TYPE postgres,
    HOST 'localhost',
    DATABASE 'access_control',
    USER 'ducklake_writer',
    PASSWORD 'simple'
);

-- Using the credentials for the AWS DuckLake Writer
CREATE OR REPLACE SECRET s3_ducklake_schema_reader_writer (
    TYPE s3,
    PROVIDER config,
    KEY_ID '<key>',
    SECRET '<secret>',
    REGION 'eu-north-1',
);

-- DuckLake config secret
CREATE OR REPLACE SECRET ducklake_writer_secret (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://ducklake-access-control/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres','SECRET': 'postgres_secret_writer'}
);

ATTACH 'ducklake:ducklake_writer_secret' as ducklake_writer;
USE ducklake_writer;

-- Let's do some stuff
CREATE TABLE IF NOT EXISTS some_schema.another_table (id INTEGER, name VARCHAR);
INSERT INTO some_schema.another_table VALUES (1, 'test'); -- Works
INSERT INTO some_schema.some_table VALUES (2, 'test2'); -- Also Works

-- Now let's be naughty and try to do something we are not allowed to do
CREATE TABLE other_table_in_main (id INTEGER, name VARCHAR); -- This unfortunately works
INSERT INTO other_table_in_main VALUES (1, 'test'); -- This doesn't work
```

In the last example, we can see that there are limitations to this approach. We can create an empty table, since this is just inserting a new record in the metadata catalog &mdash;something the DuckLake Writer is allowed to do&mdash;. The solution would be to wrap table initializations in a transaction, to make sure that the table can't be created if there is no permission to insert data.

```sql
BEGIN TRANSACTION;
CREATE TABLE other_table_in_main (id INTEGER, name VARCHAR);
INSERT INTO other_table_in_main VALUES (1, 'test'); 
COMMIT;
```

Which will throw the following error:

```console
HTTP Error:
Unable to connect to URL "https://ducklake-access-control.s3.amazonaws.com/main/other_table_in_main/ducklake-01992ec2-d9f7-745e-88e8-708e659a70be.parquet": 403 (Forbidden).

Authentication Failure - this is usually caused by invalid or missing credentials.
* No credentials are provided.
* See https://duckdb.org/docs/stable/extensions/httpfs/s3api.html
```

> The error message is the one generically used when DuckDB cannot access a specific object in S3, nothing special to DuckLake.

The **DuckLake Reader** is the simplest of them all.

```sql
DROP SECRET s3_ducklake_schema_reader_writer;
CREATE OR REPLACE SECRET s3_ducklake_table_reader (
    TYPE s3,
    PROVIDER config,
    KEY_ID '<key_id>',
    SECRET '<secret_key>',
    REGION 'eu-north-1'
);
CREATE OR REPLACE SECRET postgres_secret_reader (
    TYPE postgres,
    HOST 'localhost',
    DATABASE 'access_control',
    USER 'ducklake_reader',
    PASSWORD 'simple'
);
CREATE OR REPLACE SECRET ducklake_reader_secret (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://ducklake-access-control/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres','SECRET': 'postgres_secret_reader'}
);
ATTACH 'ducklake:ducklake_reader_secret' as ducklake_reader; 
USE ducklake_reader;

SELECT * FROM some_schema.some_table; -- Works
SELECT * FROM some_schema.another_table; -- Fails
```

The last query will print the following error:

```console
HTTP Error:
HTTP GET error on 'https://ducklake-access-control.s3.amazonaws.com/some_schema/another_table/ducklake-019929c8-c9c9-77d7-91e6-bc3c6dc87605.parquet' (HTTP 403)
```

If we try to create a table, which is just a metadata operation, the error will be the different since it will be imposed by a lack of permissions on the PostgreSQL side:

```sql
CREATE TABLE yet_another_table (a INT);
```

```console
TransactionContext Error:
Failed to commit: Failed to commit DuckLake transaction: Failed to write new table to DuckLake: Failed to prepare COPY "COPY "public"."ducklake_table" FROM STDIN (FORMAT BINARY)": ERROR:  permission denied for table ducklake_table
```

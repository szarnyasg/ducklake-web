---
layout: docu
title: Snapshots
---

Snapshots represent commits made to DuckLake.
Every snapshot performs a set of changes that alter the state of the database.
Snapshots can create tables, insert or delete data, and alter schemas.

Changes can only be made to DuckLake using snapshots.
Every set of changes must be accompanied by a snapshot.

## Listing Snapshots

The set of snapshots can be queried using the `snapshots` function. This returns a list of all snapshots and their changesets.

```sql
ATTACH 'ducklake:my_ducklake.duckdb' AS my_ducklake;
CREATE TABLE my_ducklake.people (a INTEGER, b VARCHAR);
INSERT INTO my_ducklake.people VALUES (1, 'pedro');
SELECT * FROM my_ducklake.snapshots();
```

<div class="monospace_table"></div>

| snapshot_id | snapshot_time                 | schema_version | changes                        | author | commit_message | commit_extra_info |
| ----------: | ----------------------------- | -------------: | ------------------------------ | ------ | -------------- | ----------------- |
|           0 | 2026-04-10 12:57:02.432386+02 |              0 | {schemas_created=[main]}       | NULL   | NULL           | NULL              |
|           1 | 2026-04-10 12:57:02.439404+02 |              1 | {tables_created=[main.people]} | NULL   | NULL           | NULL              |
|           2 | 2026-04-10 12:57:02.449289+02 |              1 | {inlined_insert=[1]}           | NULL   | NULL           | NULL              |

It is also possible to retrieve the latest snapshot id directly with a function.

```sql
FROM my_ducklake.current_snapshot();
```

<div class="monospace_table"></div>

|   id |
| ---: |
|    2 |

The DuckLake extension also provides a function to get the latest committed snapshot for an existing open connection. This may be useful when multiple connections are updating the same target.

```sql
FROM my_ducklake.last_committed_snapshot();
```

Which would return the following for the current connection:

<div class="monospace_table"></div>

|   id |
| ---: |
|    2 |

But if a new connection is open, it will return:

<div class="monospace_table"></div>

| id   |
| ---- |
| NULL |

## Adding a Commit Message to a Snapshot

An author and commit message can also be added in the context of a transaction. Optionally, you can also add some extra information.

```sql
ATTACH 'ducklake:my_ducklake.duckdb' AS my_ducklake;
CREATE TABLE my_ducklake.people (a INTEGER, b VARCHAR);

-- Begin Transaction
BEGIN;
INSERT INTO my_ducklake.people VALUES (1, 'pedro');
CALL my_ducklake.set_commit_message('Pedro', 'Inserting myself', extra_info => '{''foo'': 7, ''bar'': 10}');
COMMIT;
-- End transaction
```

Query the snapshots:

```sql
SELECT * FROM my_ducklake.snapshots();
```

<div class="monospace_table"></div>

| snapshot_id | snapshot_time                 | schema_version | changes                        | author | commit_message   | commit_extra_info     |
| ----------: | ----------------------------- | -------------: | ------------------------------ | ------ | ---------------- | --------------------- |
|           0 | 2026-04-10 12:57:40.148846+02 |              0 | {schemas_created=[main]}       | NULL   | NULL             | NULL                  |
|           1 | 2026-04-10 12:57:40.155454+02 |              1 | {tables_created=[main.people]} | NULL   | NULL             | NULL                  |
|           2 | 2026-04-10 12:57:40.168217+02 |              1 | {inlined_insert=[1]}           | Pedro  | Inserting myself | {'foo': 7, 'bar': 10} |

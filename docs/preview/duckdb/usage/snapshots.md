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
ATTACH 'ducklake:snapshot_test.db' AS snapshot_test;
SELECT * FROM snapshot_test.snapshots();
```

<div class="monospace_table"></div>

| snapshot_id | snapshot_time              | schema_version | changes                     | author | commit_message | commit_extra_info |
|-------------|----------------------------|----------------|-----------------------------|--------|----------------|-------------------|
| 0           | 2025-05-26 17:03:37.746+00 | 0              | {schemas_created=[main]}    | NULL   | NULL           | NULL              |
| 1           | 2025-05-26 17:03:38.66+00  | 1              | {tables_created=[main.tbl]} | NULL   | NULL           | NULL              |
| 2           | 2025-05-26 17:03:38.748+00 | 1              | {tables_inserted_into=[1]}  | NULL   | NULL           | NULL              |
| 3           | 2025-05-26 17:03:39.788+00 | 1              | {tables_deleted_from=[1]}   | NULL   | NULL           | NULL              |

It is also possible to retrieve the latest snapshot id directly whith a function.

```sql
SELECT * FROM snapshot_test.current_snapshot();
```

| id |
|---:|
| 3  |

## Adding a Commit Message to a Snapshot

An author and commit message can also be added in the context of a transaction. Optionally, you can also add some extra information.

```sql
CREATE TABLE ducklake.people (a INTEGER, b VARCHAR);

-- Begin Transaction
BEGIN;
INSERT INTO ducklake.people VALUES (1, 'pedro');
CALL ducklake.set_commit_message('Pedro', 'Inserting myself', extra_info => '{''foo'': 7, ''bar'': 10}');
COMMIT;
-- End transaction
```

| snapshot_id | snapshot_time              | schema_version | changes                       | author | commit_message   | commit_extra_info           |
|-------------|----------------------------|----------------|-------------------------------|--------|------------------|-----------------------------|
| 0           | 2025-08-18 13:10:49.636+02 | 0              | {schemas_created=[main]}      | NULL   | NULL             | NULL                        |
| 1           | 2025-08-18 13:24:15.472+02 | 1              | {tables_created=[main.t1]}    | NULL   | NULL             | NULL                        |
| 2           | 2025-08-18 13:25:24.423+02 | 2              | {tables_created=[main.people]}| NULL   | NULL             | NULL                        |
| 3           | 2025-08-18 13:26:06.38+02  | 2              | {tables_inserted_into=[2]}    | Pedro  | Inserting myself | {'foo':7, 'bar':10}         |

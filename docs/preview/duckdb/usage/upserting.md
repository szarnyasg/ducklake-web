---
layout: docu
title: Upserting
---

Upserting is the combination of updating and inserting. In database operations this usually means *do something to a record if it already exists* and *do something else if it doesn't*. Many databases support primary keys to assist with this behaviour. This is also the case with DuckDB, which allows for the syntax [`INSERT INTO ... ON CONFLICT`](https://duckdb.org/docs/stable/sql/statements/insert#on-conflict-clause).

DuckLake, on the other hand, does not support primary keys. However, the `MERGE INTO` syntax provides the same upserting functionality.

## Syntax

```sql
MERGE INTO target_table [target_alias]
    USING source_table [source_lias]
    ON (target_table.field = source_table.field)
    WHEN MATCHED THEN UPDATE [SET] | DELETE
    WHEN NOT MATCHED THEN INSERT;
```

## Usage

First, let's create a simple table.

```sql
CREATE TABLE people(id INTEGER, name VARCHAR, salary FLOAT);
INSERT INTO people VALUES (1, 'Jhon', 92_000.0), (2, 'Anna', 100_000.0);
```

The simplest upsert would be updating or inserting a whole row.
```sql
MERGE INTO people 
    USING (
        SELECT 
            unnest([3, 1]) AS id, 
            unnest(['Sarah', 'Jhon']) AS name, 
            unnest([95_000.0, 105_000.0]) AS salary
    ) AS upserts 
    ON (upserts.id = people.id) 
    WHEN MATCHED THEN UPDATE
    WHEN NOT MATCHED THEN INSERT;

FROM people;
```

| id | name  |  salary  |
|----|-------|----------|
| 1  | Jhon  | 92000.0  |
| 3  | Sarah | 95000.0  |
| 2  | Anna  | 105000.0 |


In the previous example we are updating the whole row if `id` matches. However, it is also a common pattern to receive a change set with some keys and the changed value. This is a good use for `SET`.

```sql
MERGE INTO people 
    USING (
        SELECT 
            1 AS id,  
            98_000.0 AS salary
    ) AS salary_updates 
    ON (salary_updates.id = people.id) 
    WHEN MATCHED THEN UPDATE SET salary = salary_updates.salary;

FROM people;
```

| id | name  |  salary  |
|---:|-------|---------:|
| 3  | Sarah | 95000.0  |
| 2  | Anna  | 105000.0 |
| 1  | Jhon  | 98000.0  |

Another very common pattern is to receive a delete set of rows, which may only contain ids of rows to be deleted.

```sql
MERGE INTO people 
    USING (
        SELECT 
            1 AS id,  
    ) AS deletes 
    ON (deletes.id = people.id) 
    WHEN MATCHED THEN DELETE;

FROM people;
```

| id | name  |  salary  |
|---:|-------|---------:|
| 3  | Sarah | 95000.0  |
| 2  | Anna  | 105000.0 |

Merge into also supports more complex conditions, for example for a given delete set we can decide to only remove rows that contain a `salary` bigger than a certain amount.

```sql
MERGE INTO people 
    USING (
        SELECT 
            unnest([3,2]) AS id,  
    ) AS deletes 
    ON (deletes.id = people.id) 
    WHEN MATCHED AND people.salary > 100_000.0 THEN DELETE;

FROM people;
```

| id | name  | salary  |
|---:|-------|--------:|
| 3  | Sarah | 95000.0 |

## Unsupported behaviour

Multiple `UPDATE` or `DELETE` operators are not currently supported. The following query **would not work**:
```sql
MERGE INTO people 
    USING (
        SELECT 
            unnest([3, 1]) AS id, 
            unnest(['Sarah', 'Jhon']) AS name, 
            unnest([95_000.0, 105_000.0]) AS salary
    ) AS upserts 
    ON (upserts.id = people.id) 
    WHEN MATCHED AND people.salary < 100_000.0 THEN UPDATE
    -- Second update or delete condition
    WHEN MATCHED AND people.salary > 100_000.0 THEN DELETE
    WHEN NOT MATCHED THEN INSERT;
```

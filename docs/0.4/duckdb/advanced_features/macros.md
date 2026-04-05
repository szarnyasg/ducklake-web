---
layout: docu
title: Macros
---

DuckLake supports both scalar and table macros. Macros can be created using the standard [`CREATE MACRO` syntax](https://duckdb.org/docs/current/sql/statements/create_macro).

Macros are stored in the DuckLake metadata across three catalog tables: [`ducklake_macro`]({% link docs/0.4/specification/tables/ducklake_macro.md %}), [`ducklake_macro_impl`]({% link docs/0.4/specification/tables/ducklake_macro_impl.md %}), and [`ducklake_macro_parameters`]({% link docs/0.4/specification/tables/ducklake_macro_parameters.md %}).

Macros support [time travel]({% link docs/0.4/duckdb/usage/time_travel.md %}), so attaching at a previous snapshot will reflect the macros that existed at that point in time.

## Scalar Macros

Scalar macros return a single value.

```sql
CREATE MACRO add_values(a, b) AS a + b;
SELECT add_values(40, 2);
```

## Table Macros

Table macros return a table.

```sql
CREATE MACRO filtered_table(threshold) AS TABLE
    SELECT *
    FROM my_table
    WHERE value > threshold;
SELECT * FROM filtered_table(100);
```

## Default Parameters

Macros can define default values for parameters.

```sql
CREATE MACRO add_with_default(a, b := 10) AS a + b;
SELECT add_with_default(5);
```

## Typed Parameters

Macros can specify types for their parameters.

```sql
CREATE MACRO typed_add(a INTEGER, b INTEGER) AS a + b;
```

## Dropping Macros

Macros can be dropped using `DROP MACRO` or `DROP MACRO TABLE` for table macros.

```sql
DROP MACRO add_values;
DROP MACRO TABLE filtered_table;
```

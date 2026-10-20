---
layout: docu
title: Troubleshooting
---

This guide explains how to troubleshoot certain issues with DuckLake.
Besides the issues described on this page, see also the [“Unsupported Features” page]({% link docs/stable/duckdb/unsupported_features.md %}).

## Connecting to an Older DuckLake

An existing 1.0 catalog can be used without migration.
If you request `DUCKLAKE_VERSION '1.1'` for that catalog without enabling migration, you get the following error message:

```console
Invalid Input Error:
DuckLake catalog version mismatch: catalog version is 1.0, but the extension requires version 1.1. To automatically migrate, set AUTOMATIC_MIGRATION to TRUE when attaching.
```

To work around this, add the `AUTOMATIC_MIGRATION` flag to the `ATTACH` command:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake (AUTOMATIC_MIGRATION true);
```

## Connecting to a Read-Only DuckLake

Read-only 1.0 and 1.1 catalogs can be attached without migration.
If you try to migrate a read-only catalog, you can get the following error message:

```console
Invalid Input Error:
Failed to rename inlined-data metadata columns of "ducklake_inlined_data_1_1" while migrating to v1.1: Cannot execute statement of type "ALTER" on database "__ducklake_metadata_my_ducklake" which is attached in read-only mode!
```

Catalogs from before 1.0 and catalogs labeled `1.1-dev1` must be migrated before use, including read-only use.
Migrate a writable copy of the catalog, then attach the migrated copy in read-only mode.
See [“Upgrading to DuckLake 1.1”]({% link docs/stable/duckdb/migrations/upgrading_to_ducklake_1_1.md %}) for details.

## Requesting an Older Catalog Version

Requesting version 1.0 for a catalog that has already been migrated produces the following error:

```console
Invalid Input Error:
DuckLake catalog version is '1.1', which is newer than the requested version '1.0'. Cannot downgrade a DuckLake catalog.
```

Remove `DUCKLAKE_VERSION '1.0'` from `ATTACH` or run `RESET ducklake_default_version;` if the global setting was pinned.

---
layout: docu
redirect_from:
- /docs
- /docs/
title: Documentation
---

Welcome to the DuckLake documentation. This documentation has two parts:

* **[The DuckLake specification]({% link docs/stable/specification/introduction.md %}):** The specification of the DuckLake lakehouse format. It describes the SQL tables and queries used to define the catalog database.
* **[The `ducklake` DuckDB extension]({% link docs/stable/duckdb/introduction.md %}):** User guide for the `ducklake` DuckDB extension. It presents the features of DuckLake through examples.

## DuckLake Clients

The `ducklake` DuckDB extension serves as the reference implementation for DuckLake clients.
Additionally, DuckLake currently has implementations for the following libraries (at various levels of maturity):

* [DataFusion](https://github.com/hotdata-dev/datafusion-ducklake)
* [Spark](https://github.com/motherduckdb/ducklake-spark)
* [Trino](https://github.com/awitten1/trino-ducklake)
* [PostgreSQL (`pg_duckdb`)](https://github.com/relytcloud/pg_ducklake)

## Single File Documentation

You can download the documentation as a single file:

* [DuckLake documentation in Markdown](https://blobs.duckdb.org/docs/ducklake-docs.md)
* [DuckLake documentation as a PDF](https://blobs.duckdb.org/docs/ducklake-docs.pdf)

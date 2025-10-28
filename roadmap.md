---
layout: default
title: Development Roadmap
body_class: roadmap blog_typography post
max_page_width: small
toc: false
---

<div class="wrap pagetitle">
  <h1>Development Roadmap</h1>
</div>

## Overview

The DuckLake project is governed by the [non-profit DuckDB Foundation](https://duckdb.org/foundation/).

## Planned Features (Last Updated: September 2025)

This section lists the features that we plan to work on this year. The list was compiled by the DuckLake maintainers and is based on the long-term vision for the project and general interactions with users in the open-source community.

- Documentation regarding [access control](https://github.com/duckdb/ducklake/discussions/249) in DuckLake. ✅
- Migration guides for moving from DuckDB to DuckLake, covering both DuckDB and PostgreSQL catalogs. ✅
- Optimize [heavily deleted tables](https://github.com/duckdb/ducklake/issues/331). ✅
- Cleanup of orphan files. ✅
- [Geometry/geospatial types](https://github.com/duckdb/ducklake/discussions/83). ✅
- Fine-grained update conflicts at the file level to avoid many retries when multiple writers are updating the same table.
- Data inlining with PostgreSQL as a catalog.
- Scalar and table macros.
- Read performance improvements regarding Parquet Bloom filters and metadata scans. See issue [#389](https://github.com/duckdb/ducklake/discussions/389) and [#404](https://github.com/duckdb/ducklake/issues/404).

Please note that there are **no guarantees** that a particular feature will be released within the next release. Everything on this page is subject to change without notice.

## Future Work

These are some of the items that we plan to support in the future:

- [Allow primary key syntax without really enforcing it](https://github.com/duckdb/ducklake/discussions/323), similar to what other OLAP engines do (e.g., [BigQuery](https://cloud.google.com/bigquery/docs/primary-foreign-keys)).
- User defined types.
- Variant types.
- Fixed-size arrays.
- Default values that are not literals.

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

## Planned Features (Last Updated: November 2025)

This section lists the features that we plan to work on before DuckLake v1.0. The list was compiled by the DuckLake maintainers and is based on the long-term vision for the project and general interactions with users in the open-source community.

- Data inlining with PostgreSQL as a catalog.
- Inline of deletes/updates.
- Scalar and table macros.
- Expressions as default values for columns.
- Variant types.
- Incremental compaction for large volumes of small files.
- Revisit some internals, namely `DATA_PATH`, `add_data_files` and option scopes.

Please note that there are **no guarantees** that a particular feature will be released within the next release. Everything on this page is subject to change without notice.

## Future Work

These are some of the items that we plan to support in the future:

- PostgreSQL performance improvements: reduce number of roundtrips and explore optimizations for large metadata.
- User defined types.
- Protected snapshots.
- Branching/merge functionality [see](https://github.com/duckdb/ducklake/discussions/194).
- Read performance improvements regarding Parquet Bloom filters and metadata scans. See issue [#389](https://github.com/duckdb/ducklake/discussions/389) and [#404](https://github.com/duckdb/ducklake/issues/404).
- [Allow primary key syntax without really enforcing it](https://github.com/duckdb/ducklake/discussions/323), similar to what other OLAP engines do (e.g., [BigQuery](https://cloud.google.com/bigquery/docs/primary-foreign-keys)).
- Fixed-size arrays.

If you are interested in prioritizing some of this work, [get in touch with DuckDB Labs](https://duckdblabs.com/contact/]). 

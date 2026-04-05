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

_(Last Updated: April 2026)_

The DuckLake project is governed by the [non-profit DuckDB Foundation](https://duckdb.org/foundation/).
The Foundation and [DuckDB Labs](https://duckdblabs.com/) are not funded by external investors (e.g., venture capital).
Instead, the Foundation is funded by contributions from its members, while DuckDB Labs' revenue is based on commercial support and feature prioritization services.
These extend to the [`ducklake` DuckDB extension]({% link docs/preview/duckdb/introduction.md %}).

## Planned Features

This section lists the features that we plan to work on for future DuckLake releases.
The list was compiled by the DuckLake maintainers and is based on the long-term vision for the project and general interactions with users in the open-source community.

TODO: review these

- Incremental compaction for large volumes of small files.
- Revisit some internals, namely `DATA_PATH`, `add_data_files` and option scopes.

Please note that there are **no guarantees** that a particular feature will be released within the next release. Everything on this page is subject to change without notice.

## Future Work / Looking for Funding

These are some of the items that we plan to support in the future. If you are interested in prioritizing some of this work, [get in touch with DuckDB Labs](https://duckdblabs.com/contact/).

- PostgreSQL performance improvements: reduce number of roundtrips and explore optimizations for large metadata.
- User defined types.
- Protected snapshots.
- [Branching/merge functionality](https://github.com/duckdb/ducklake/discussions/194).
- Read performance improvements regarding Parquet Bloom filters and metadata scans. See issues [#389](https://github.com/duckdb/ducklake/discussions/389) and [#404](https://github.com/duckdb/ducklake/issues/404).
- [Allow `PRIMARY KEY` syntax without enforcing it](https://github.com/duckdb/ducklake/discussions/323), similar to what other OLAP engines do (e.g., [BigQuery](https://cloud.google.com/bigquery/docs/primary-foreign-keys)).
- Fixed-size arrays.
- Improved [MySQL support]({% link docs/preview/duckdb/usage/choosing_a_catalog_database.md %}#mysql).

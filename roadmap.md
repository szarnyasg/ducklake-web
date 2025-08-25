---
layout: default
title: Development Roadmap
body_class: roadmap blog_typography post
redirect_from:
- /docs/stable/dev/roadmap
- /docs/stable/dev/roadmap/
- /docs/preview/dev/roadmap
- /docs/preview/dev/roadmap/
max_page_width: small
toc: false
---

<div class="wrap pagetitle">
  <h1>Development Roadmap</h1>
</div>

## Overview

The DuckDB project is governed by the [non-profit DuckDB Foundation](https://duckdb.org/foundation/).
The Foundation and [DuckDB Labs](https://duckdblabs.com) are not funded by external investors (e.g., venture capital).
Instead, the Foundation is funded by contributions from its [members](https://duckdb.org/foundation/#supporters),
while DuckDB Labs' revenue is based on [commercial support and feature prioritization services](https://duckdblabs.com/#support).

## Planned Features (Last Updated: August 2025)

This section lists the features that we plan to work on this year. The list was compiled by the DuckLake maintainers and is based on the long-term vision for the project and general interactions with users in the open source community. 

- Documentation regarding access control in DuckLake.
- Migration guides for moving from DuckDB to DuckLake, covering both DuckDB and PostgreSQL catalogs.
- Optimize heavily deleted tables.
- Data inlining with PostgreSQL as a catalog.
- Cleanup of orphan files.
- Allow primary key syntax without really enforcing it, similar to what other OLAP engines do (e.g. [BigQuery](https://cloud.google.com/bigquery/docs/primary-foreign-keys)).
- Geometry/Geospatial types.

Please note that there are **no guarantees** that a particular feature will be released within the next year. Everything on this page is subject to change without notice.

## Future Work

These are some of the items that we plan to support in the future. If you would like to expedite the development of these features, please [get in touch with DuckDB Labs](https://duckdblabs.com/contact/).

- Scalar and table macros.
- User defined types.
- Variant types.
- Fixed-size arrays.
- Default values that are not literals.

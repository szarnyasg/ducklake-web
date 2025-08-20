---
layout: default
redirect_from:
- /cal
- /release-calendar
title: Release Calendar
body_class: release-calendar blog_typography post
max_page_width: medium
toc: false
---

<div class="wrap pagetitle">
  <h1>Release Calendar</h1>
</div>

DuckLake follows [semantic versioning](https://semver.org/spec/v2.0.0.html).
Larger new features are introduced in minor versions,
while patch versions mostly contain bugfixes.

DuckLake 1.0 is planned to be released in 2026.

## Past Releases

In the following, we list DuckLake's past releases.

<!-- markdownlint-disable MD034 MD055 MD056 MD058 -->

{% assign latest_version_number = "0.0" %}

{% for row in site.data.past_releases %}
  {% if row.version_number > latest_version_number %}
    {% assign latest_version_number = row.version_number %}
  {% endif %}
{% endfor %}

| Date | Version | Announcement post |
|:-----|--------:|-------------------|
{% for row in site.data.past_releases %}
  {%- if row.version_number == latest_version_number %}
    {% assign docs_version = "stable" %}
  {% else %}
    {% assign docs_version = row.version_number %}
  {% endif -%}
  | {{ row.release_date }} | [{{ row.version_number }}](/docs/{{ docs_version }}) | [post]({{ row.blog_post }}) |
{% endfor %}

<!-- markdownlint-enable MD034 MD055 MD056 MD058 -->

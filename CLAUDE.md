# DuckLake Documentation Site

## Project Overview

This is the documentation website for [DuckLake](https://github.com/duckdb/ducklake), a lakehouse format built on DuckDB. It's a Jekyll site hosted on GitHub Pages.

## Repository Structure

```
docs/
  preview/                      # In-progress docs for next release (default target)
  stable/                       # Published docs for current release
  (both share the same subdirectory layout below)
    ├── index.md                # Landing page
    ├── specification/          # DuckLake format specification
    │   ├── introduction.md
    │   ├── data_types.md
    │   ├── queries.md
    │   └── tables/             # Catalog table definitions
    └── duckdb/                 # DuckDB extension user guide
        ├── introduction.md
        ├── usage/              # Core usage docs (connecting, storage, config, etc.)
        ├── advanced_features/  # Partitioning, views, constraints, encryption, etc.
        ├── maintenance/        # Checkpointing, cleanup, snapshots, file merging
        ├── metadata/           # Adding/listing files
        ├── guides/             # Tutorials (access control, backups, object storage)
        └── migrations/         # Migration guides (e.g., duckdb_to_ducklake)
_data/
  menu_docs_stable.json         # Navigation sidebar for stable docs
scripts/                        # Utility scripts (Python, Bash)
CONTRIBUTING.md                 # Style guide and contribution rules
```

## Key Conventions

### Documentation Style (see CONTRIBUTING.md for full details)

- **Front matter**: Every doc page needs `layout: docu` and a `title` property. Do not repeat the title as an h1.
- **Headers**: Use h2 (`##`), h3 (`###`), h4 (`####`) only. Chicago-style headline capitalization.
- **Cross-references**: Use Jekyll link tags: `{% link docs/<version>/path/to/page.md %}` (match the docs version you're editing).
- **SQL style**: UPPERCASE keywords, lowercase functions, snake_case names, 4-space indent, semicolons.
- **Code blocks**: `sql` for SQL, `python` for Python, `batch` for shell with `$` prompt, `bash` for shell without prompt, `text` for output, `console` for errors.
- **Callout boxes**: `> Note`, `> Warning`, `> Tip`, `> Bestpractice`, `> Deprecated`.
- **Lists**: Use `*` for unordered lists, 4-space indent for nesting.
- **File naming**: `snake_case.md`.
- **New pages**: Create the `.md` file and add an entry to the matching `_data/menu_docs_<version>.json`.

### Python Scripts

- Formatted with `black --skip-string-normalization` (single quotes preferred).
- Virtual environment at `venv/` — activate with `source venv/bin/activate`.

### Linting

Run `scripts/lint.sh` to check everything:
- `markdownlint` for Markdown files
- `black` for Python scripts
- `vale` for prose style

## Common Tasks

### Adding Documentation for a DuckLake Feature

1. Determine if it extends an existing page or needs a new one.
2. Edit/create the Markdown file in the appropriate `docs/stable/` subdirectory.
3. If creating a new page, add it to `_data/menu_docs_preview.json` in the correct position.
4. Follow the style guide in CONTRIBUTING.md.
5. Run `scripts/lint.sh` to verify.

### Automated Doc Updates

`scripts/update_docs.py` automates documentation updates from merged PRs in duckdb/ducklake:

```bash
python scripts/update_docs.py 277                           # single issue (preview)
python scripts/update_docs.py 277,286                       # multiple issues
python scripts/update_docs.py --full-batch                  # all matching open issues
python scripts/update_docs.py 277 --dry-run                 # print prompt only
python scripts/update_docs.py 277 --docs-version stable     # target stable docs
python scripts/update_docs.py 277 --model opus              # use a different model
```

## GitHub Repos

- **This repo**: `duckdb/ducklake-web` (documentation site)
- **DuckLake core**: `duckdb/ducklake` (the lakehouse format + DuckDB extension)
- Issues with `[ducklake/#NNN]` in the title link to PRs in the core repo that need doc updates.

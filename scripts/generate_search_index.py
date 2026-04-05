"""
Generate a DuckDB search index for the DuckLake documentation.

Parses all markdown files under docs/stable/ and docs/preview/,
chunks them (per-H2 section), and builds a DuckDB file with a
pre-built FTS index.

Usage:
    python scripts/generate_search_index.py [--output PATH] [--validate]
"""

import argparse
import os
import re
import sys

import duckdb
import frontmatter

# ---------------------------------------------------------------------------
# Anchor / slug generation (matches Kramdown defaults)
# ---------------------------------------------------------------------------


def slugify(text):
    """Convert heading text to an anchor slug matching Kramdown's rules."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # strip non-alphanumeric except - and _
    slug = re.sub(r'[\s]+', '-', slug)  # spaces to hyphens
    slug = slug.strip('-')
    return slug


# ---------------------------------------------------------------------------
# Breadcrumb from file path
# ---------------------------------------------------------------------------

BREADCRUMB_RENAMES = {
    'sql': 'SQL',
    'duckdb': 'DuckDB',
    'ducklake': 'DuckLake',
    'fts': 'FTS',
    'api': 'API',
}


def breadcrumb_segment(segment):
    """Prettify a single path segment for breadcrumb display."""
    if segment in BREADCRUMB_RENAMES:
        return BREADCRUMB_RENAMES[segment]
    return segment.replace('_', ' ').title()


def build_breadcrumb(filepath, version):
    """Build a breadcrumb string from a docs file path.

    e.g. docs/stable/duckdb/usage/connecting.md -> DuckDB > Usage > Connecting
    """
    relative = filepath.removeprefix(f'docs/{version}/').removesuffix('.md')
    parts = relative.split('/')
    if parts and parts[-1] in ('index', 'overview'):
        parts = parts[:-1]
    return ' > '.join(breadcrumb_segment(p) for p in parts)


# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------


def page_slug(filepath, version):
    """Strip docs/<version>/ prefix and .md suffix to get a clean page slug."""
    return filepath.removeprefix(f'docs/{version}/').removesuffix('.md')


def make_unique_anchor(anchor, seen_anchors):
    """Deduplicate anchors on the same page (matching Kramdown behavior)."""
    if anchor not in seen_anchors:
        seen_anchors[anchor] = 0
        return anchor
    seen_anchors[anchor] += 1
    return f'{anchor}-{seen_anchors[anchor]}'


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_page(filepath, version, title, body):
    """Split a page into one chunk per ## heading."""
    chunks = []
    base_url = '/' + filepath.removesuffix('.md')
    slug = page_slug(filepath, version)
    breadcrumb = build_breadcrumb(filepath, version)
    seen_anchors = {}

    # Split on ## headings
    parts = re.split(r'^(##)\s+(.+)$', body, flags=re.MULTILINE)

    intro = parts[0].strip()

    # If there are no H2 headings, treat the whole page as one chunk
    if len(parts) == 1:
        chunks.append(
            {
                'chunk_id': f'{version}/{slug}',
                'page_title': title,
                'section': None,
                'breadcrumb': breadcrumb,
                'url': base_url,
                'version': version,
                'text': body.strip(),
            }
        )
        return chunks

    # Intro chunk (content before first H2)
    if intro:
        chunks.append(
            {
                'chunk_id': f'{version}/{slug}',
                'page_title': title,
                'section': None,
                'breadcrumb': breadcrumb,
                'url': base_url,
                'version': version,
                'text': intro,
            }
        )

    # H2 sections
    i = 1
    while i < len(parts):
        _marker = parts[i]
        heading = parts[i + 1].strip()
        content = parts[i + 2].strip() if i + 2 < len(parts) else ''
        i += 3

        anchor = make_unique_anchor(slugify(heading), seen_anchors)
        text = f'## {heading}\n\n{content}' if content else f'## {heading}'

        chunks.append(
            {
                'chunk_id': f'{version}/{slug}#{anchor}',
                'page_title': title,
                'section': heading,
                'breadcrumb': breadcrumb,
                'url': f'{base_url}#{anchor}',
                'version': version,
                'text': text,
            }
        )

    return chunks


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def process_file(filepath, version):
    """Parse a single markdown file and return its chunks."""
    with open(filepath, 'r') as f:
        post = frontmatter.load(f)

    title = post.get('title', '')
    if not title:
        return []

    body = post.content
    return chunk_page(filepath, version, title, body)


def collect_chunks(docs_dir, version):
    """Walk a docs version directory and collect all chunks."""
    chunks = []
    for root, _dirs, files in os.walk(docs_dir):
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            filepath = os.path.join(root, fname)
            rel_path = os.path.relpath(filepath, '.').replace(os.sep, '/')
            try:
                chunks.extend(process_file(rel_path, version))
            except Exception as e:
                print(f'  Warning: failed to process {rel_path}: {e}')
    return chunks


# ---------------------------------------------------------------------------
# DuckDB index building
# ---------------------------------------------------------------------------


def build_duckdb(chunks, output_path):
    """Create the DuckDB file with docs_chunks table and FTS index."""
    if os.path.exists(output_path):
        os.remove(output_path)

    con = duckdb.connect(output_path)

    con.execute("""
        CREATE TABLE docs_chunks (
            chunk_id   VARCHAR PRIMARY KEY,
            page_title VARCHAR NOT NULL,
            section    VARCHAR,
            breadcrumb VARCHAR,
            url        VARCHAR NOT NULL,
            version    VARCHAR NOT NULL,
            text       TEXT NOT NULL
        )
    """)

    con.executemany(
        """
        INSERT INTO docs_chunks (chunk_id, page_title, section, breadcrumb, url, version, text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                c['chunk_id'],
                c['page_title'],
                c['section'],
                c['breadcrumb'],
                c['url'],
                c['version'],
                c['text'],
            )
            for c in chunks
        ],
    )

    row_count = con.execute('SELECT count(*) FROM docs_chunks').fetchone()[0]
    print(f'Inserted {row_count} chunks')

    # Build FTS index
    con.execute('INSTALL fts')
    con.execute('LOAD fts')
    con.execute("""
        PRAGMA create_fts_index(
            'docs_chunks',
            'chunk_id',
            'page_title', 'section', 'text',
            stemmer   = 'porter',
            stopwords = 'english',
            ignore    = '(\\.|[^a-zA-Z0-9_])+',
            lower     = 1,
            overwrite = 1
        )
    """)
    print('FTS index built')

    con.close()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate(output_path):
    """Run a smoke-test query against the generated index."""
    con = duckdb.connect(output_path, read_only=True)
    con.execute('LOAD fts')

    results = con.execute("""
        SELECT chunk_id, page_title, score
        FROM (
            SELECT *,
                   fts_main_docs_chunks.match_bm25(chunk_id, 'attach catalog') AS score
            FROM docs_chunks
        )
        WHERE score IS NOT NULL
        ORDER BY score DESC
        LIMIT 5
    """).fetchall()

    con.close()

    if not results:
        print("VALIDATION FAILED: no results for 'attach catalog'")
        return False

    print("Validation passed — top 5 results for 'attach catalog':")
    for chunk_id, page_title, score in results:
        print(f'  {score:8.4f}  {chunk_id}  ({page_title})')
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description='Build DuckLake docs search index')
    parser.add_argument(
        '--output',
        default='data/docs-search.duckdb',
        help='Output .duckdb file path (default: data/docs-search.duckdb)',
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run a smoke-test FTS query after building',
    )
    args = parser.parse_args()

    versions = [
        ('docs/stable', 'stable')
    ]

    all_chunks = []
    for docs_dir, version in versions:
        if not os.path.isdir(docs_dir):
            print(f'Skipping {version}: {docs_dir} not found')
            continue
        print(f'Processing {version}...')
        chunks = collect_chunks(docs_dir, version)
        print(f'  {len(chunks)} chunks from {version}')
        all_chunks.extend(chunks)

    if not all_chunks:
        print('No chunks found — nothing to build')
        sys.exit(1)

    print(f'\nTotal: {len(all_chunks)} chunks')
    print(f'Building {args.output}...')
    build_duckdb(all_chunks, args.output)

    if args.validate:
        print()
        if not validate(args.output):
            sys.exit(1)

    print(f'\nDone. Output: {args.output}')


if __name__ == '__main__':
    main()

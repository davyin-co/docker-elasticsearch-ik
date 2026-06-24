#!/usr/bin/env python3
"""Discover Elasticsearch versions that have a matching IK plugin available.

Outputs a JSON object {"version": ["8.19.17", "8.18.8", ...]} to ./matrix.json
for consumption by the GitHub Actions workflow via ${{ fromJSON(...) }}.

Filter policy (conservative):
  - Only semver tags (X.Y.Z) — drops `latest`, sha256 digests, pre-release suffixes.
  - Only major versions in ALLOWED_MAJOR (history: 5.x/6.x are EOL).
  - Keep the most recent MINORS_PER_MAJOR minor versions per major.
  - Keep the most recent PATCHES_PER_MINOR patch versions per minor.
  - Hard cap at MAX_TOTAL to bound CI minutes.

Both the ES tag list and the IK plugin index must agree on a version; versions
missing from either side are silently dropped.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

# --- Configuration ---------------------------------------------------------

ES_REPO = "library/elasticsearch"
IK_INDEX_URL = "https://release.infinilabs.com/analysis-ik/stable/"

ALLOWED_MAJOR: set[int] = {7, 8, 9}
MINORS_PER_MAJOR: int = 2
PATCHES_PER_MINOR: int = 2
MAX_TOTAL: int = 12

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
IK_ZIP_RE = re.compile(r"elasticsearch-analysis-ik-(\d+\.\d+\.\d+)\.zip")

HTTP_TIMEOUT = 30
USER_AGENT = "elasticsearch-ik-discoverer/1.0 (+https://github.com)"


# --- Networking helpers ----------------------------------------------------

def _http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def _http_get_json(url: str) -> dict:
    return json.loads(_http_get(url))


# --- Source fetchers -------------------------------------------------------

def fetch_dockerhub_tags(repo: str) -> list[str]:
    """Return all tag names for a Docker Hub repository (paginated)."""
    tags: list[str] = []
    url: str | None = f"https://hub.docker.com/v2/repositories/{repo}/tags/?page_size=100"
    pages = 0
    while url and pages < 20:  # safety cap: 2000 tags is plenty
        data = _http_get_json(url)
        tags.extend(t["name"] for t in data.get("results", []))
        url = data.get("next")
        pages += 1
    return tags


def fetch_ik_versions(index_url: str = IK_INDEX_URL) -> set[str]:
    """Parse the IK plugin directory listing and return available version strings."""
    html = _http_get(index_url)
    return {m.group(1) for m in IK_ZIP_RE.finditer(html)}


# --- Filtering -------------------------------------------------------------

def filter_versions(
    versions: Iterable[str],
    minors_per_major: int,
    patches_per_minor: int,
    max_total: int,
) -> list[str]:
    """Apply the conservative retention policy and return a sorted, capped list."""
    bucket: dict[int, dict[int, set[int]]] = {}
    for v in versions:
        m = SEMVER_RE.match(v)
        if not m:
            continue
        major, minor, patch = (int(g) for g in m.groups())
        if major not in ALLOWED_MAJOR:
            continue
        bucket.setdefault(major, {}).setdefault(minor, set()).add(patch)

    selected: list[str] = []
    for major in sorted(bucket, reverse=True):
        minors = sorted(bucket[major], reverse=True)[:minors_per_major]
        for minor in minors:
            patches = sorted(bucket[major][minor], reverse=True)[:patches_per_minor]
            for patch in patches:
                selected.append(f"{major}.{minor}.{patch}")

    # Stable desc sort, then truncate.
    selected.sort(key=lambda v: tuple(int(x) for x in v.split(".")), reverse=True)
    return selected[:max_total]


# --- Entrypoint ------------------------------------------------------------

def main() -> int:
    try:
        ik_versions = fetch_ik_versions()
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"::error::Failed to fetch IK index from {IK_INDEX_URL}: {exc}", file=sys.stderr)
        return 1
    if not ik_versions:
        print(f"::error::No IK plugin versions parsed from {IK_INDEX_URL}", file=sys.stderr)
        return 1

    try:
        es_tags = fetch_dockerhub_tags(ES_REPO)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"::error::Failed to fetch Docker Hub tags for {ES_REPO}: {exc}", file=sys.stderr)
        return 1

    # Optional workflow_dispatch override — union extra requested versions
    # before filtering (they will still be dropped if not in ik_versions).
    extra_raw = os.environ.get("DISCOVER_EXTRA_VERSIONS", "").strip()
    extra = [v.strip() for v in extra_raw.split(",") if v.strip()]

    candidates = [v for v in es_tags if SEMVER_RE.match(v) and v in ik_versions]
    candidates.extend(v for v in extra if v not in candidates)
    matrix = filter_versions(candidates, MINORS_PER_MAJOR, PATCHES_PER_MINOR, MAX_TOTAL)

    if not matrix:
        print("::error::No buildable versions after filtering", file=sys.stderr)
        return 1

    dropped_extras = [v for v in extra if v not in matrix]
    if dropped_extras:
        print(
            f"::warning::Requested override version(s) not built "
            f"(missing ES tag or IK plugin): {dropped_extras}",
            file=sys.stderr,
        )

    Path("matrix.json").write_text(json.dumps({"version": matrix}))
    print(f"Discovered {len(matrix)} versions: {matrix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Furkan Köykıran
"""
scripts/verify_foundation.py

Foundation Verification Suite for fcode.
Validates public repository integrity:
1. Markdown relative hyperlink and asset reference resolution.
2. Clean working tree hygiene (no temporary, backup, or cache files).
3. Canonical SPDX AGPL-3.0-or-later license headers on source scripts.
"""

import glob
import os
import re
import sys

sys.dont_write_bytecode = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def verify_markdown_hyperlinks():
    """Verify that all relative markdown links and image sources exist on disk."""
    print("Checking Invariant: Markdown hyperlink and asset resolution...")
    md_files = glob.glob(os.path.join(BASE_DIR, "**", "*.md"), recursive=True)
    broken_links = []

    for md_file in md_files:
        if "/.git/" in md_file:
            continue
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        links = re.findall(r'\[(?:[^\]]*)\]\(([^)]+)\)', content)
        img_links = re.findall(r'<img[^>]+src=[\"\']([^\"\']+)[\"\']', content)

        dir_name = os.path.dirname(md_file)
        for link in links + img_links:
            # Skip anchors, protocol URLs, mailto
            if link.startswith(("#", "http://", "https://", "mailto:")):
                continue
            clean_link = link.split("#")[0]
            if not clean_link:
                continue
            target_path = os.path.normpath(os.path.join(dir_name, clean_link))
            if not os.path.exists(target_path):
                rel_src = os.path.relpath(md_file, BASE_DIR)
                broken_links.append((rel_src, link, os.path.relpath(target_path, BASE_DIR)))

    if broken_links:
        for src, link, tgt in broken_links:
            print(f"  [FAIL] Broken link in {src}: {link} -> {tgt}", file=sys.stderr)
        raise AssertionError(f"Found {len(broken_links)} broken relative links in markdown documentation.")

    print(f"  [PASS] All relative links and image paths resolve cleanly across {len(md_files)} markdown files.")


def verify_repository_hygiene():
    """Verify that no temporary, backup, or cache files exist in the repository."""
    print("Checking Invariant: Repository hygiene (no temporary or cache files)...")
    forbidden_extensions = (".pyc", ".swp", ".swo", "~", ".tmp", ".bak")
    forbidden_names = (".DS_Store", "Thumbs.db")

    cache_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            if f.endswith(forbidden_extensions) or f in forbidden_names:
                cache_files.append(os.path.relpath(os.path.join(root, f), BASE_DIR))

    if cache_files:
        for cf in cache_files:
            print(f"  [FAIL] Stray file detected: {cf}", file=sys.stderr)
        raise AssertionError(f"Detected {len(cache_files)} temporary or cache files.")

    print("  [PASS] Repository working tree is clean of temporary and cache files.")


def verify_spdx_headers():
    """Verify that source scripts contain canonical SPDX license identifiers."""
    print("Checking Invariant: Canonical SPDX license headers...")
    script_files = glob.glob(os.path.join(BASE_DIR, "scripts", "*.py"))
    missing = []

    for sf in script_files:
        with open(sf, "r", encoding="utf-8") as f:
            header = f.read(500)
        if "SPDX-License-Identifier: AGPL-3.0-or-later" not in header:
            missing.append(os.path.relpath(sf, BASE_DIR))

    if missing:
        for m in missing:
            print(f"  [FAIL] Missing SPDX AGPL-3.0-or-later header: {m}", file=sys.stderr)
        raise AssertionError(f"Found {len(missing)} scripts lacking canonical SPDX license headers.")

    print(f"  [PASS] Canonical SPDX AGPL-3.0-or-later headers verified across {len(script_files)} scripts.")


def main():
    print("==================================================")
    print("Running fcode Foundation Verification Suite")
    print("==================================================")
    try:
        verify_markdown_hyperlinks()
        verify_repository_hygiene()
        verify_spdx_headers()
        print("==================================================")
        print("ALL FOUNDATION INVARIANTS VERIFIED (100% PASS)")
        print("==================================================")
    except AssertionError as e:
        print(f"\n[FAIL] Assertion Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

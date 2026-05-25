#!/usr/bin/env python3
"""Validate local markdown links + image references under highs/quantum/docs/.

Resolves every Markdown link / image whose target is a relative path,
asserts the file exists and (if an anchor is present) the anchor lives in the
target file as an h1/h2/h3 heading. Skips http(s) / mailto / non-local refs.

Usage:
    python3 highs/quantum/docs/check_links.py [docs_root]

Exit codes:
    0   all references resolve
    1   one or more broken links / missing files
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Iterable


_MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)")
_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$", re.MULTILINE)


def slugify(heading: str) -> str:
    """GitHub-flavored anchor slug. Approximation — covers our docs' usage."""
    s = heading.lower()
    s = re.sub(r"[^\w\s\-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def collect_anchors(path: pathlib.Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {slugify(m) for m in _HEADING.findall(text)}


def iter_links(text: str) -> Iterable[str]:
    for m in _MD_LINK.finditer(text):
        yield m.group(1)


def is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "#"))


def check_file(md_path: pathlib.Path, docs_root: pathlib.Path) -> list[str]:
    """Return a list of error strings for `md_path`. Empty = clean."""
    errors: list[str] = []
    text = md_path.read_text(encoding="utf-8", errors="replace")
    for link in iter_links(text):
        if is_external(link):
            continue
        if "#" in link:
            target_part, anchor = link.split("#", 1)
        else:
            target_part, anchor = link, ""
        target_part = target_part.strip()
        if not target_part:
            continue
        target = (md_path.parent / target_part).resolve()
        try:
            target.relative_to(docs_root.resolve().parent.parent.parent)
        except ValueError:
            # Allow references that escape the docs root (e.g. ../python/README.md);
            # just check existence.
            pass
        if not target.exists():
            errors.append(f"  {md_path.relative_to(docs_root)}: missing {link!r}")
            continue
        if anchor and target.suffix.lower() == ".md":
            anchors = collect_anchors(target)
            if slugify(anchor) not in anchors:
                errors.append(
                    f"  {md_path.relative_to(docs_root)}: anchor #{anchor} "
                    f"not found in {target.relative_to(docs_root.parent.parent.parent)}"
                )
    return errors


def main(argv: list[str]) -> int:
    docs_root = pathlib.Path(argv[1] if len(argv) > 1 else
                             pathlib.Path(__file__).parent).resolve()
    md_files = sorted(docs_root.glob("*.md"))
    if not md_files:
        print(f"No Markdown files under {docs_root}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for md in md_files:
        errors = check_file(md, docs_root)
        all_errors.extend(errors)

    if all_errors:
        print("Broken references:", file=sys.stderr)
        for e in all_errors:
            print(e, file=sys.stderr)
        return 1

    print(f"OK — {len(md_files)} files clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

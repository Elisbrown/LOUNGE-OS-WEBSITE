#!/usr/bin/env python3
"""Copy the latest LoungeOS release (version and date) into scripts/site/release.json.

The installers are published as GitHub releases of this repository, and the
download buttons point at releases/latest. This keeps the version number written
on the site (download page, homepage, help centre, JSON-LD softwareVersion,
llms.txt) in line with that release, so nobody has to edit it by hand. The SEO
refresh GitHub Action runs it when a release is published and every day, and
rebuilds the pages when the version changed. Browsers also read the latest
release live (app.js), so the page is right even before the rebuild.

    python3 scripts/site/sync_version.py   # exit 0: unchanged, 10: changed, 1: unreachable

When GitHub can't be reached, release.json is left as it is.
"""
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "release.json")
REPO = os.environ.get("RELEASE_REPO", "Elisbrown/lounge-os-website")
URL = f"https://api.github.com/repos/{REPO}/releases/latest"


def fetch():
    req = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "loungeos-site-build"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    try:
        rel = fetch()
    except Exception as e:  # noqa: BLE001
        print(f"Could not read the latest release: {e}", file=sys.stderr)
        return 1
    m = re.search(r"\d+\.\d+\.\d+", rel.get("tag_name") or rel.get("name") or "")
    if not m:
        print(f"No version in the latest release tag {rel.get('tag_name')!r}", file=sys.stderr)
        return 1
    new = {"version": m.group(0), "published": (rel.get("published_at") or "")[:10],
           "url": rel.get("html_url") or f"https://github.com/{REPO}/releases/latest"}
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except (OSError, ValueError):
        old = None
    if old == new:
        print(f"Latest release unchanged: {new['version']}")
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
        f.write("\n")
    print(f"Latest release: {(old or {}).get('version')} -> {new['version']}")
    return 10


if __name__ == "__main__":
    sys.exit(main())

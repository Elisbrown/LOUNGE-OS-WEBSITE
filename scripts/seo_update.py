#!/usr/bin/env python3
"""Keep loungeos.app's crawl files fresh and truthful.

Run from the repository root (CI runs it on every push to main and daily):

    python3 scripts/seo_update.py              # regenerate files
    python3 scripts/seo_update.py --indexnow-file urls.txt
                                               # also write changed URLs for IndexNow
    python3 scripts/seo_update.py --ping urls.txt
                                               # submit those URLs to IndexNow

What it does
- sitemap.xml: every indexable page, with <lastmod> taken from the last git
  commit that touched the page (bot commits excluded), plus hreflang alternates.
- Page dates: updates "dateModified" in JSON-LD and <time data-auto="modified">
  on each page to that same git date, so on-page dates match the sitemap.
- blog/feed.xml: RSS feed of blog posts, newest first.
- robots.txt: allow search engines and AI assistants, point to the sitemaps.
- llms.txt: a plain-text map of the site for AI assistants.
- Asset versions: links to /style.css and /app.js carry ?v=<content hash>, so
  browsers and CDNs fetch the new file as soon as it changes instead of pairing
  new HTML with a stale cached stylesheet.

Dates only change when a page's content changes. Search engines ignore (and can
distrust) lastmod values that move without real edits, so nothing here fakes
freshness: publish or update content and the dates follow automatically.

Standard library only.
"""
import argparse
import datetime as dt
import functools
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from xml.sax.saxutils import escape

SITE = "https://loungeos.app"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_MARK = "[seo-bot]"
INDEXNOW_KEY = "8391080daa0a00470dfef794afac6a58"
EXCLUDE_DIRS = {".git", ".github", "scripts", "Screenshots", "images", "node_modules"}
EXCLUDE_FILES = {"404.html"}
VERSIONED_ASSETS = ("style.css", "app.js")
FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def last_modified(rel):
    """Date of the last non-bot commit touching the file; today if uncommitted or locally edited."""
    if git("status", "--porcelain", "--", rel):
        return dt.date.today()
    out = git("log", "-1", "--format=%cs", "--invert-grep", f"--grep={re.escape(BOT_MARK)}", "--", rel)
    return dt.date.fromisoformat(out) if out else dt.date.today()


@functools.lru_cache(maxsize=None)
def asset_version(name, root=ROOT):
    with open(os.path.join(root, name), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]


def version_links(src, root=ROOT):
    """Rewrite href="/style.css" and src="/app.js" (with or without an old ?v=)
    to carry the current content hash of the file."""
    for name in VERSIONED_ASSETS:
        src = re.sub(r'((?:href|src)=")/?%s(?:\?v=[0-9a-f]*)?"' % re.escape(name),
                     rf'\g<1>/{name}?v={asset_version(name, root)}"', src)
    return src


def og_slug(url):
    p = re.sub(r"^https?://[^/]+", "", url).strip("/")
    p = re.sub(r"/index$", "", re.sub(r"\.html$", "", p))
    return p.replace("/", "-") or "home"


SOCIAL_TAG = re.compile(r'\n?[ \t]*<meta\s+(?:property|name)="(?:og:image(?::[a-z_]+)?|twitter:(?:card|title|description|image|image:alt))"'
                        r'\s+content="[^"]*"\s*/?>|\n?[ \t]*<link\s+rel="image_src"[^>]*>')


def social_tags(src, root=ROOT):
    """Give the page its own share card (images/og/<slug>.webp, made by scripts/og/)
    and the tags each platform reads: og:* for WhatsApp, Facebook, LinkedIn,
    Telegram, Slack and iMessage; twitter:* for X; image_src for older scrapers."""
    canonical = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', src)
    anchor = re.search(r'\n([ \t]*)<meta\s+property="og:description"\s+content="([^"]*)"\s*/?>', src)
    title = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', src)
    if not (canonical and anchor and title):
        return src
    slug = og_slug(canonical.group(1))
    if not os.path.exists(os.path.join(root, "images", "og", slug + ".webp")):
        return src
    img, ind, desc, t = f"{SITE}/images/og/{slug}.webp", anchor.group(1), anchor.group(2), title.group(1)
    tags = [f'<meta property="og:image" content="{img}" />',
            f'<meta property="og:image:secure_url" content="{img}" />',
            '<meta property="og:image:type" content="image/webp" />',
            '<meta property="og:image:width" content="1200" />',
            '<meta property="og:image:height" content="630" />',
            f'<meta property="og:image:alt" content="{t}" />',
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{t}" />',
            f'<meta name="twitter:description" content="{desc}" />',
            f'<meta name="twitter:image" content="{img}" />',
            f'<meta name="twitter:image:alt" content="{t}" />',
            f'<link rel="image_src" href="{img}" />']
    src = SOCIAL_TAG.sub("", src)
    anchor = re.search(r'<meta\s+property="og:description"\s+content="[^"]*"\s*/?>', src)
    return src[:anchor.end()] + "".join("\n" + ind + x for x in tags) + src[anchor.end():]


def version_all_pages():
    """Apply version_links and social_tags to every HTML page, including noindex ones.
    Returns the number changed."""
    changed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in filenames:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dirpath, f)
            src = open(path, encoding="utf-8").read()
            new = social_tags(version_links(src))
            if new != src:
                open(path, "w", encoding="utf-8").write(new)
                changed += 1
    return changed


def url_for(rel):
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[: -len("index.html")]
    return SITE + "/" + rel


def meta(src, pattern):
    m = re.search(pattern, src, re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else ""


def discover():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith("."))
        for f in sorted(filenames):
            if not f.endswith(".html") or f in EXCLUDE_FILES:
                continue
            path = os.path.join(dirpath, f)
            rel = os.path.relpath(path, ROOT)
            src = open(path, encoding="utf-8").read()
            if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', src, re.I):
                continue
            canonical = meta(src, r'<link\s+rel="canonical"\s+href="([^"]+)"')
            pages.append({
                "rel": rel,
                "path": path,
                "src": src,
                "url": canonical or url_for(rel),
                "title": meta(src, r"<title>(.*?)</title>"),
                "description": meta(src, r'<meta\s+name="description"\s+content="([^"]*)"'),
                "lang": meta(src, r'<html\s+lang="([^"]+)"') or "en",
                "published": meta(src, r'<meta\s+property="article:published_time"\s+content="([^"]+)"'),
                "is_post": 'property="og:type" content="article"' in src,
                "alternates": re.findall(r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"', src),
                "lastmod": last_modified(rel),
            })
    return pages


def fmt_date(d, lang):
    if lang.startswith("fr"):
        return f"{d.day} {FR_MONTHS[d.month - 1]} {d.year}"
    return f"{EN_MONTHS[d.month - 1]} {d.day}, {d.year}"


def sync_page_dates(page):
    """Make on-page modified dates match the git date. Returns True if the file changed."""
    d = page["lastmod"]
    iso = d.isoformat()
    src = page["src"]
    new = re.sub(r'("dateModified":\s*")\d{4}-\d{2}-\d{2}(")', rf"\g<1>{iso}\2", src)
    new = re.sub(r'(<meta\s+property="article:modified_time"\s+content=")[^"]*("\s+data-auto="modified")',
                 rf"\g<1>{iso}\2", new)
    new = re.sub(r'<time datetime="[^"]*" data-auto="modified">[^<]*</time>',
                 f'<time datetime="{iso}" data-auto="modified">{fmt_date(d, page["lang"])}</time>', new)
    if new != src:
        open(page["path"], "w", encoding="utf-8").write(new)
        page["src"] = new
        return True
    return False


def write_sitemap(pages):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p in sorted(pages, key=lambda p: (p["url"] != SITE + "/", p["url"])):
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(p['url'])}</loc>")
        lines.append(f"    <lastmod>{p['lastmod'].isoformat()}</lastmod>")
        for lang, href in p["alternates"]:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{escape(lang)}" href="{escape(href)}"/>')
        lines.append("  </url>")
    lines.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def write_feed(pages):
    posts = sorted([p for p in pages if p["is_post"]], key=lambda p: (p["published"], p["url"]), reverse=True)
    if not posts:
        return
    def rfc822(d):
        return dt.datetime.combine(dt.date.fromisoformat(d) if isinstance(d, str) else d,
                                   dt.time(8, 0), tzinfo=dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    build = max(p["lastmod"] for p in posts)
    items = []
    for p in posts:
        title = p["title"].split(" | ")[0]
        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <link>{escape(p['url'])}</link>
      <guid isPermaLink="true">{escape(p['url'])}</guid>
      <description>{escape(p['description'])}</description>
      <pubDate>{rfc822(p['published'] or p['lastmod'])}</pubDate>
      <dc:language>{escape(p['lang'])}</dc:language>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>LoungeOS Blog</title>
    <link>{SITE}/blog/</link>
    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Guides on restaurant, bar and lounge POS systems, loss prevention, inventory, accounting and running hospitality businesses in Africa.</description>
    <language>en</language>
    <lastBuildDate>{rfc822(build)}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    os.makedirs(os.path.join(ROOT, "blog"), exist_ok=True)
    open(os.path.join(ROOT, "blog", "feed.xml"), "w", encoding="utf-8").write(feed)


AI_AND_SEARCH_AGENTS = [
    "Googlebot", "Bingbot", "Applebot", "DuckDuckBot", "YandexBot",
    "OAI-SearchBot", "ChatGPT-User", "GPTBot",
    "Claude-SearchBot", "Claude-User", "ClaudeBot",
    "PerplexityBot", "Perplexity-User",
    "Google-Extended", "Applebot-Extended", "Meta-ExternalAgent", "CCBot",
]


def write_robots():
    agents = "\n".join(f"User-agent: {a}" for a in AI_AND_SEARCH_AGENTS)
    robots = f"""# robots.txt for loungeos.app. Generated by scripts/seo_update.py; edit that script, not this file.
# Search engines and AI assistants are welcome to crawl and cite LoungeOS pages.

User-agent: *
{agents}
Allow: /
Disallow: /scripts/
Disallow: /seo/

Sitemap: {SITE}/sitemap.xml
Sitemap: {SITE}/blog/feed.xml
"""
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)


LLMS_HEADER = """# LoungeOS

> LoungeOS is point of sale (POS) and business management software for every kind of business that sells: restaurants, bars, lounges, cafés, nightclubs, hotels, retail shops, supermarkets and more. It is made by Sigalix (https://sigalix.com) and built in Cameroon. It runs in the web app at https://app.loungeos.app and as Windows, Mac and Android apps, with one LoungeOS account everywhere. The Windows and Mac apps keep selling without internet and sync when the connection comes back.

Key facts:
- Version 2.1.4. English and French interface. Help centre with step-by-step guides: https://loungeos.app/help/ (French: https://loungeos.app/fr/aide/).
- Where it runs: the web app in any modern browser (https://app.loungeos.app); Windows 10 and 11 (64-bit); Mac (Apple Silicon and Intel); Android 7.0 or later. Downloads: https://loungeos.app/download/. Phones and tablets on the same Wi-Fi can use a Windows or Mac till through their browser. The web app and the Android app need internet.
- Account: one LoungeOS account per person, with email and password or Continue with Google. A setup wizard asks for the business type, name, logo, currency, taxes, payment methods and opening hours, and suggests categories to tick. No licence keys: a Windows or Mac till signs in by showing a short code that the owner confirms at account.loungeos.app/link. The owner invites staff by email; staff can also use a quick PIN on a shared till. Roles and permissions per staff member.
- Modules: POS for touch and mouse on any screen size, tables and orders, kitchen and bar screens, payment methods each business creates (cash, MTN Mobile Money, Orange Money, card, bank transfer and others), receipts on 58 mm and 80 mm thermal printers or as PDF, inventory with stock movements and low-stock alerts, suppliers, expenses with your own categories, accounting (chart of accounts, journal), reports, staff roles and an activity log, a cloud copy of all data with daily full backups. Also: customer tabs (pay later) with balances and part payments; QR code table ordering where guests order from their phone and staff accept on the till (Business and Pro); several branches with a copy of the menu, tables, settings and team, and an all-branches sales overview (Pro); an Android app with notifications by role and a home-screen widget.
- Offline: a Windows or Mac till keeps selling without internet and syncs automatically when it is back online. After 7 days without syncing it becomes read-only until it reconnects, with a warning during the last 2 days. Read-only means past orders, reports, printing and exports still work, but no new sales or edits. When a subscription ends, LoungeOS becomes read-only until it is renewed. Nothing is ever deleted.
- Pricing: every plan starts with a 14-day free trial with Business features and no payment up front. Starter US$10/month (6,000 FCFA): 2 users, 2 devices, POS, tables, kitchen and bar screens, inventory, customer tabs, receipts, daily reports. Business US$25/month (15,000 FCFA): 5 users, 5 devices, adds expenses, accounting, weekly and monthly reports, QR code table ordering. Pro US$50/month (30,000 FCFA): unlimited users, 10+ devices, several branches with an all-branches overview, priority support. Coming soon: shifts and cash control, email alerts, payroll. Paying yearly gives 2 months free: US$100, US$250 or US$500 a year (60,000, 150,000 or 300,000 FCFA). Visitors in Cameroon see FCFA; everyone else sees US$. Payment by Mobile Money (MTN, Orange), card or PayPal at https://account.loungeos.app, charged in FCFA.
- Not included today: integrated card processing, delivery-platform integrations, hotel PMS folio posting, e-invoicing/fiscal device connections.
- Contact: info@sigalix.com (inquiries), billing@sigalix.com (billing), support@loungeos.app, +237 679 690 703.
"""


def write_llms(pages):
    def line(p):
        title = p["title"].split(" | ")[0]
        return f"- [{title}]({p['url']}): {p['description']}"
    groups = [
        ("Product", lambda u: u in (SITE + "/", SITE + "/pricing/", SITE + "/download/", SITE + "/faq/", SITE + "/about/", SITE + "/contact/")),
        ("Features", lambda u: u.startswith(SITE + "/features/")),
        ("Solutions by venue", lambda u: re.search(r"/(restaurant|bar|lounge|nightclub|hotel|cafe)-pos/$", u)),
        ("Countries", lambda u: re.search(r"/(africa|cameroon|nigeria|ghana|south-africa)/$", u)),
        ("Help centre", lambda u: u.startswith((SITE + "/help/", SITE + "/fr/aide/"))),
        ("Guides (English)", lambda u: u.startswith(SITE + "/blog/") and u != SITE + "/blog/"),
        ("En français", lambda u: u.startswith(SITE + "/fr/")),
    ]
    out = [LLMS_HEADER]
    seen = set()
    for name, test in groups:
        items = [p for p in sorted(pages, key=lambda p: p["url"]) if test(p["url"]) and p["url"] not in seen]
        if not items:
            continue
        seen.update(p["url"] for p in items)
        out.append(f"## {name}\n")
        out.extend(line(p) for p in items)
        out.append("")
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(out).rstrip() + "\n")


def previous_lastmods():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        return {}
    xml = open(path, encoding="utf-8").read()
    return dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml))


def ping_indexnow(urls):
    if not urls:
        print("IndexNow: nothing to submit")
        return
    body = json.dumps({"host": "loungeos.app", "key": INDEXNOW_KEY,
                       "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow: submitted {len(urls)} URL(s), HTTP {r.status}")
    except Exception as e:  # never fail the build over a ping
        print(f"IndexNow: submission failed ({e})", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indexnow-file", help="write URLs whose lastmod changed to this file")
    ap.add_argument("--ping", help="submit the URLs listed in this file to IndexNow and exit")
    args = ap.parse_args()

    if args.ping:
        urls = [u.strip() for u in open(args.ping) if u.strip()] if os.path.exists(args.ping) else []
        ping_indexnow(urls)
        return

    before = previous_lastmods()
    pages = discover()
    changed_files = [p["rel"] for p in pages if sync_page_dates(p)]
    write_sitemap(pages)
    write_feed(pages)
    write_robots()
    write_llms(pages)
    # After discover(): lastmod is already read from git, so these edits don't move it.
    versioned = version_all_pages()

    changed_urls = [p["url"] for p in pages if before.get(p["url"]) != p["lastmod"].isoformat()]
    print(f"{len(pages)} pages in sitemap; {len(changed_files)} page date(s) synced; "
          f"{versioned} page(s) re-versioned; {len(changed_urls)} URL(s) new or updated")
    if args.indexnow_file:
        with open(args.indexnow_file, "w") as f:
            f.write("\n".join(changed_urls))


if __name__ == "__main__":
    main()

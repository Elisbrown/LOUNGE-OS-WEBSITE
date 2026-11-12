#!/usr/bin/env python3
"""Static page generator for loungeos.app content pages.

Reads content/**/*.md (YAML front matter + Markdown) and writes
<repo>/<url>/index.html for each page, plus /blog/, using the site's
style.css and app.js. See README.md in this folder.

    pip install markdown pyyaml beautifulsoup4
    python3 scripts/site/build.py          # from the repository root
"""
import datetime as dt
import html
import json
import math
import os
import re
import sys

import markdown
import yaml
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from seo_update import social_tags, version_links  # noqa: E402
CONTENT = os.path.join(HERE, "content")
SITE = "https://loungeos.app"
TODAY = dt.date(2026, 10, 8)
APP_VERSION = "2.1.4"
SIGNUP = "https://app.loungeos.app/login"  # sign-up is on the sign-in page
WIN_DOWNLOAD = "/download/"
# Hand-maintained pages that generated pages may reference as hreflang alternates
MANUAL_PAGES = {"/"}
LENIENT = bool(os.environ.get("LENIENT"))

ORG_ID = SITE + "/#organization"
WEBSITE_ID = SITE + "/#website"
SOFTWARE_ID = SITE + "/#software"

FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre"]

T = {
    "en": {
        "home": "Home", "blog": "Blog", "start_trial": "Start free trial",
        "see_pricing": "See pricing",
        "trust": "14-day free trial · No payment up front · Sells offline on Windows and Mac",
        "by": "By", "team": "LoungeOS Team", "published": "Published",
        "updated": "Updated", "min_read": "min read", "takeaways": "Key takeaways",
        "toc": "In this guide", "related": "Keep reading", "explore": "Explore more",
        "cta_title": "Run your next service on LoungeOS",
        "cta_text": "Create your account, answer the setup wizard and your business is ready on day one. Try it free for 14 days with Business features. No payment up front.",
        "cta_btn2": "Download for Windows",
        "read_more": "Read guide →", "learn_more": "Learn more →",
        "faq_heading": "Frequently asked questions",
        "og_locale": "en_US",
        "help": "Help centre", "help_for": "For", "help_toc": "On this page",
        "help_stuck": "Stuck on a step? Write to support@loungeos.app or WhatsApp +237 679 690 703 and say which page you are on.",
        "help_back": "All help articles",
    },
    "fr": {
        "home": "Accueil", "blog": "Blog", "start_trial": "Essai gratuit",
        "see_pricing": "Voir les tarifs",
        "trust": "Essai gratuit de 14 jours · Sans paiement à l'avance · Vente hors ligne sur Windows et Mac",
        "by": "Par", "team": "l'équipe LoungeOS", "published": "Publié le",
        "updated": "Mis à jour le", "min_read": "min de lecture", "takeaways": "Points clés",
        "toc": "Dans ce guide", "related": "À lire aussi", "explore": "Découvrir aussi",
        "cta_title": "Faites votre prochain service avec LoungeOS",
        "cta_text": "Créez votre compte, répondez à l'assistant de configuration et votre activité est prête dès le premier jour. Essai gratuit de 14 jours avec les fonctionnalités Business, sans paiement à l'avance.",
        "cta_btn2": "Télécharger pour Windows",
        "read_more": "Lire le guide →", "learn_more": "En savoir plus →",
        "faq_heading": "Questions fréquentes",
        "og_locale": "fr_FR",
        "help": "Centre d'aide", "help_for": "Pour", "help_toc": "Sur cette page",
        "help_stuck": "Bloqué à une étape ? Écrivez à support@loungeos.app ou sur WhatsApp au +237 679 690 703 en précisant la page.",
        "help_back": "Tous les articles d'aide",
    },
}


def fmt_date(d, lang):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d)
    if lang == "fr":
        return f"{d.day} {FR_MONTHS[d.month - 1]} {d.year}"
    return d.strftime("%B %-d, %Y")


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- data
def load_pages():
    pages = []
    for root, _, files in os.walk(CONTENT):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            raw = open(os.path.join(root, f), encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
            if not m:
                raise SystemExit(f"missing front matter: {f}")
            meta = yaml.safe_load(m.group(1))
            meta["body_md"] = m.group(2)
            meta["src"] = f
            meta.setdefault("lang", "en")
            meta.setdefault("type", "page")
            meta.setdefault("alternates", {})
            for k in ("published", "modified"):
                if k in meta and isinstance(meta[k], (dt.date,)):
                    meta[k] = meta[k].isoformat()
            meta.setdefault("modified", meta.get("published", TODAY.isoformat()))
            pages.append(meta)
    by_url = {p["url"]: p for p in pages}
    # hreflang: make alternates bidirectional
    for p in pages:
        for lang, url in list(p["alternates"].items()):
            other = by_url.get(url)
            if not other:
                if url in MANUAL_PAGES or LENIENT:
                    continue
                raise SystemExit(f"{p['url']}: alternate {url} not found")
            other["alternates"].setdefault(p["lang"], p["url"])
    for p in pages:
        if p["alternates"]:
            p["alternates"].setdefault(p["lang"], p["url"])
    return pages, by_url


# ---------------------------------------------------------------- html parts
def webp_size(path):
    """(width, height) of a WebP file, read from its header (VP8, VP8L or VP8X)."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(30)
    except OSError:
        return None
    if head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        return None
    kind = head[12:16]
    if kind == b"VP8 ":
        return (int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF)
    if kind == b"VP8L":
        b = head[21:25]
        return (1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
    if kind == b"VP8X":
        return (1 + int.from_bytes(head[24:27], "little"), 1 + int.from_bytes(head[27:30], "little"))
    return None


SCREENS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "images", "screens"))


def img_tag(name, alt, hero=False, sizes="(max-width: 800px) 100vw, 960px"):
    attrs = 'fetchpriority="high"' if hero else 'loading="lazy"'
    w, h = webp_size(os.path.join(SCREENS_DIR, name + ".webp")) or (1600, 861)
    small = os.path.exists(os.path.join(SCREENS_DIR, name + "-800.webp"))
    srcset = (f'srcset="/images/screens/{name}-800.webp 800w, /images/screens/{name}.webp {w}w" sizes="{sizes}" '
              if small else "")
    tall = ' class="shot-tall"' if h > w else ""
    return (f'<img src="/images/screens/{name}.webp" {srcset}'
            f'width="{w}" height="{h}" alt="{esc(alt)}"{tall} {attrs} decoding="async" />')


CHEVRON = ('<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<polyline points="6 9 12 15 18 9"></polyline></svg>')
GLOBE = ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px" aria-hidden="true">'
         '<circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" />'
         '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" /></svg>')
ARROW = ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12" />'
         '<polyline points="12 5 19 12 12 19" /></svg>')

LANG_OPTIONS = [("en", "English"), ("fr", "Français"), ("es", "Español"), ("de", "Deutsch"),
                ("zh-CN", "中文"), ("ar", "العربية"), ("hi", "हिन्दी"), ("pt", "Português"),
                ("ru", "Русский"), ("ja", "日本語")]

NAV = {
    "en": {
        "badge": "POS &amp; Business",
        "links": [("Home", "/"), ("Features", "/features/")],
        "solutions": ("Solutions", [("Restaurants", "/restaurant-pos/"), ("Bars", "/bar-pos/"),
                                    ("Lounges", "/lounge-pos/"), ("Nightclubs", "/nightclub-pos/"),
                                    ("Hotels", "/hotel-pos/"), ("Cafés &amp; Fast Food", "/cafe-pos/"),
                                    ("Shops &amp; Mini-Markets", "/retail-pos/"),
                                    ("Cameroon", "/cameroon/"), ("Africa", "/africa/")]),
        "after": [("Pricing", "/pricing/"), ("Download", "/download/")],
        "resources": ("Resources", [("Blog", "/blog/"), ("FAQ", "/faq/"),
                                    ("Help centre", "/help/"),
                                    ("About", "/about/"), ("Contact", "/contact/"),
                                    ("Français", "/fr/")]),
        "cta": "Start free trial",
    },
    "fr": {
        "badge": "Logiciel de caisse",
        "links": [("Accueil", "/fr/"), ("Fonctionnalités", "/fr/fonctionnalites/")],
        "solutions": ("Solutions", [("Restaurants", "/fr/logiciel-caisse-restaurant/"),
                                    ("Bars, lounges &amp; boîtes de nuit", "/fr/logiciel-gestion-bar-lounge/"),
                                    ("Boutiques &amp; supérettes", "/fr/logiciel-caisse-boutique/"),
                                    ("Hôtels", "/hotel-pos/"),
                                    ("Cameroun", "/fr/cameroun/"),
                                    ("Côte d'Ivoire", "/fr/cote-divoire/"),
                                    ("Sénégal", "/fr/senegal/"),
                                    ("Afrique francophone", "/fr/afrique/")]),
        "after": [("Tarifs", "/fr/tarifs/"), ("Télécharger", "/fr/telecharger/")],
        "resources": ("Ressources", [("Blog", "/blog/"), ("FAQ", "/fr/faq/"),
                                     ("Centre d'aide", "/fr/aide/"),
                                     ("Contact", "/contact/"),
                                     ("English", "/")]),
        "cta": "Essai gratuit",
    },
}


def dropdown(label, items):
    links = "\n".join(f'              <a href="{u}">{t}</a>' for t, u in items)
    return f"""          <div class="nav-dropdown">
            <button type="button" class="nav-dropdown-toggle" aria-haspopup="true">{label} {CHEVRON}</button>
            <div class="nav-dropdown-menu">
{links}
            </div>
          </div>"""


def nav_html(lang):
    n = NAV[lang]
    home = "/fr/" if lang == "fr" else "/"
    links = "\n".join(f'          <a href="{u}">{t}</a>' for t, u in n["links"])
    after = "\n".join(f'          <a href="{u}">{t}</a>' for t, u in n["after"])
    opts = "\n".join(
        f'              <option value="{v}"{" selected" if v == lang else ""}>{t}</option>'
        for v, t in LANG_OPTIONS)
    sel_label = "Choisir la langue" if lang == "fr" else "Select Language"
    return f"""    <a class="skip-link" href="#main-content">{'Aller au contenu' if lang == 'fr' else 'Skip to content'}</a>
    <nav class="navbar" id="navbar" aria-label="{'Navigation principale' if lang == 'fr' else 'Main Navigation'}">
      <div class="nav-content">
        <div class="nav-left">
          <a href="{home}" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 0.75rem;">
            <img src="/images/logo/loungeos-logo.svg" alt="LoungeOS" width="148" height="26" class="nav-logo" />
            <span class="nav-badge">{n['badge']}</span>
          </a>
        </div>

        <div class="nav-links" id="navLinks">
{links}
{dropdown(*n['solutions'])}
{after}
{dropdown(*n['resources'])}
        </div>

        <div class="nav-cta" style="display: flex; align-items: center; gap: 1rem">
          <div class="lang-selector">
            {GLOBE}
            <select id="customLangSelect" aria-label="{sel_label}" onchange="changeLanguage(this.value)">
{opts}
            </select>
          </div>
          <a href="{SIGNUP}" class="btn btn-primary btn-sm" id="navCtaBtn">{n['cta']}</a>
        </div>

        <button class="menu-toggle" id="menuToggle" aria-label="{'Ouvrir le menu' if lang == 'fr' else 'Toggle navigation menu'}">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </nav>"""


FOOTER = {
    "en": {
        "tagline": 'Point of sale and business management for every business that sells. Made by <a href="https://sigalix.com">Sigalix</a>, built in Cameroon, used across Africa and beyond.',
        "chips": ["Web, Windows, Mac &amp; Android", "English &amp; French", "Sells offline on desktop"],
        "cols": [
            ("Product", [("Features", "/features/"), ("Pricing", "/pricing/"), ("Download", "/download/"),
                         ("Offline POS", "/features/offline-pos/"),
                         ("Kitchen Display System", "/features/kitchen-display-system/"),
                         ("Inventory", "/features/inventory-management/"),
                         ("Accounting", "/features/restaurant-accounting/")]),
            ("Solutions", [("Restaurant POS", "/restaurant-pos/"), ("Bar POS", "/bar-pos/"),
                           ("Lounge POS", "/lounge-pos/"), ("Nightclub POS", "/nightclub-pos/"),
                           ("Hotel POS", "/hotel-pos/"), ("Café &amp; Fast Food POS", "/cafe-pos/"),
                           ("Retail &amp; Shop POS", "/retail-pos/")]),
            ("Countries", [("Cameroon", "/cameroon/"), ("Nigeria", "/nigeria/"), ("Ghana", "/ghana/"),
                           ("South Africa", "/south-africa/"), ("Africa", "/africa/"),
                           ("Cameroun (FR)", "/fr/cameroun/"), ("Côte d'Ivoire (FR)", "/fr/cote-divoire/"),
                           ("Sénégal (FR)", "/fr/senegal/")]),
            ("Resources", [("Blog", "/blog/"), ("FAQ", "/faq/"), ("Help centre", "/help/"),
                           ("About", "/about/"),
                           ("Contact", "/contact/"), ("Privacy Policy", "/privacy.html"),
                           ("Terms of Service", "/terms.html"), ("Accessibility", "/accessibility.html"),
                           ("Legal", "/legal.html")]),
        ],
        "rights": "All rights reserved.",
        "cta": "Start free trial",
    },
    "fr": {
        "tagline": 'Logiciel de caisse et de gestion pour toutes les entreprises qui vendent. Conçu par <a href="https://sigalix.com">Sigalix</a> au Cameroun, utilisé en Afrique et au-delà.',
        "chips": ["Web, Windows, Mac &amp; Android", "Français &amp; anglais", "Vente hors ligne sur ordinateur"],
        "cols": [
            ("Produit", [("Fonctionnalités", "/fr/fonctionnalites/"), ("Tarifs", "/fr/tarifs/"),
                         ("Télécharger", "/fr/telecharger/"), ("FAQ", "/fr/faq/")]),
            ("Solutions", [("Logiciel de caisse restaurant", "/fr/logiciel-caisse-restaurant/"),
                           ("Logiciel bar &amp; lounge", "/fr/logiciel-gestion-bar-lounge/"),
                           ("Logiciel caisse boutique", "/fr/logiciel-caisse-boutique/"),
                           ("Afrique francophone", "/fr/afrique/")]),
            ("Pays", [("Cameroun", "/fr/cameroun/"), ("Côte d'Ivoire", "/fr/cote-divoire/"),
                      ("Sénégal", "/fr/senegal/"), ("Cameroon (EN)", "/cameroon/"),
                      ("Nigeria (EN)", "/nigeria/"), ("Ghana (EN)", "/ghana/")]),
            ("Ressources", [("Blog", "/blog/"), ("Centre d'aide", "/fr/aide/"),
                            ("À propos", "/about/"),
                            ("Contact", "/contact/"), ("Confidentialité", "/privacy.html"),
                            ("Conditions", "/terms.html"), ("Mentions légales", "/legal.html")]),
        ],
        "rights": "Tous droits réservés.",
        "cta": "Commencer l'essai gratuit",
    },
}

CHECK = ('<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'aria-hidden="true"><polyline points="20 6 9 17 4 12" /></svg>')


def footer_html(lang):
    f = FOOTER[lang]
    chips = "\n".join(f"            <span>{CHECK} {c}</span>" for c in f["chips"])
    cols = []
    for title, links in f["cols"]:
        ls = "\n".join(f'          <a href="{u}">{t}</a>' for t, u in links)
        cols.append(f'        <div class="footer-col">\n          <h3>{title}</h3>\n{ls}\n        </div>')
    cols = "\n".join(cols)
    return f"""    <footer class="footer">
      <div class="footer-grid footer-grid-wide">
        <div class="footer-brand">
          <img src="/images/logo/loungeos-logo-white.svg" alt="LoungeOS" width="159" height="28" class="footer-logo" />
          <p>{f['tagline']}</p>
          <div class="footer-worldwide">
{chips}
          </div>
          <p class="footer-contact">
            <a href="mailto:support@loungeos.app">support@loungeos.app</a><br />
            <a href="mailto:info@sigalix.com">info@sigalix.com</a><br />
            <a href="tel:+237679690703">+237 679 690 703</a>
          </p>
        </div>
{cols}
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 LoungeOS. {f['rights']}</p>
        <a href="{SIGNUP}" class="btn btn-outline-light btn-sm" id="footerCtaBtn">{f['cta']} {ARROW}</a>
      </div>
    </footer>"""


ANALYTICS = """    <!-- Microsoft Clarity -->
    <script type="text/javascript">
      (function (c, l, a, r, i, t, y) {
        c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
        t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
        y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
      })(window, document, "clarity", "script", "x9n1mwb8c5");
    </script>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-TNP53ZZW7K"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() { dataLayer.push(arguments); }
      gtag("js", new Date());
      gtag("config", "G-TNP53ZZW7K");
    </script>
    <!-- Usercentrics CMP -->
    <script id="usercentrics-cmp" src="https://app.usercentrics.eu/browser-ui/latest/loader.js" data-settings-id="SSwfY4ZtHuL22V" async></script>"""


def tail_scripts(lang):
    return f"""    <div id="google_translate_element" style="display: none"></div>
    <script type="text/javascript">
      function googleTranslateElementInit() {{
        new google.translate.TranslateElement(
          {{ pageLanguage: "{lang}", autoDisplay: false }},
          "google_translate_element",
        );
      }}
    </script>
    <script defer type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
    <script defer src="/app.js"></script>"""


# ---------------------------------------------------------------- schema
ORG = {
    "@type": "Organization",
    "@id": ORG_ID,
    "name": "LoungeOS",
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/images/logo/loungeos-icon-512.png", "width": 512, "height": 512},
    "image": SITE + "/images/og-loungeos.jpg",
    "description": "LoungeOS makes point of sale (POS) and business management software for every kind of business that sells: restaurants, bars, lounges, cafés, nightclubs, hotels, retail shops, supermarkets and more. LoungeOS is made by Sigalix.",
    "email": "info@sigalix.com",
    "telephone": "+237679690703",
    "address": {"@type": "PostalAddress", "addressCountry": "CM"},
    "areaServed": ["CM", "Africa", "Worldwide"],
    "knowsLanguage": ["en", "fr"],
    "contactPoint": [
        {"@type": "ContactPoint", "contactType": "customer support", "email": "support@loungeos.app",
         "telephone": "+237679690703", "availableLanguage": ["English", "French"]},
        {"@type": "ContactPoint", "contactType": "sales", "email": "info@sigalix.com",
         "telephone": "+237689699688", "availableLanguage": ["English", "French"]},
        {"@type": "ContactPoint", "contactType": "billing support", "email": "billing@sigalix.com"},
    ],
    "parentOrganization": {"@type": "Organization", "name": "Sigalix", "url": "https://sigalix.com",
                           "email": "info@sigalix.com"},
}
WEBSITE = {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE + "/", "name": "LoungeOS",
           "publisher": {"@id": ORG_ID}, "inLanguage": ["en", "fr"]}


def offer(name, price, cur, months=None):
    o = {"@type": "Offer", "name": name, "price": str(price), "priceCurrency": cur,
         "availability": "https://schema.org/InStock", "url": SITE + "/pricing/"}
    if months:
        o["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": str(price),
                                   "priceCurrency": cur, "billingDuration": f"P{months}M",
                                   "referenceQuantity": {"@type": "QuantitativeValue", "value": months,
                                                         "unitCode": "MON"}}
    return o


# Plans and prices (keep in sync with PLANS in /app.js). Same features in every
# currency. Visitors in Cameroon see FCFA, everyone else US$. Yearly = 10 months
# (2 months free). Every plan starts with a free trial with Business features.
TRIAL_DAYS = 14
PRICES = [
    # key, name, users (None = unlimited), devices, US$/month, US$/year, FCFA/month, FCFA/year
    ("starter", "Starter", 2, "2", 10, 100, 6000, 60000),
    ("business", "Business", 5, "5", 25, 250, 15000, 150000),
    ("pro", "Pro", None, "10+", 50, 500, 30000, 300000),
]


def plan_offers():
    offers = [offer(f"{TRIAL_DAYS}-day free trial (Business features)", 0, "USD")]
    for _, name, _, _, usd_m, usd_y, xaf_m, xaf_y in PRICES:
        offers += [offer(f"{name} monthly", usd_m, "USD", 1),
                   offer(f"{name} yearly", usd_y, "USD", 12),
                   offer(f"{name} monthly (Cameroon)", xaf_m, "XAF", 1),
                   offer(f"{name} yearly (Cameroon)", xaf_y, "XAF", 12)]
    return offers


SOFTWARE = {
    "@type": "SoftwareApplication",
    "@id": SOFTWARE_ID,
    "name": "LoungeOS",
    "applicationCategory": "BusinessApplication",
    "applicationSubCategory": "Point of sale (POS) and business management software",
    "operatingSystem": "Windows 10 and 11 (64-bit), macOS (Apple Silicon and Intel), Android 7.0 or later, any modern web browser",
    "softwareVersion": APP_VERSION,
    "downloadUrl": SITE + "/download/",
    "installUrl": SITE + "/download/",
    "url": SITE + "/",
    "inLanguage": ["en", "fr"],
    "publisher": {"@id": ORG_ID},
    "description": "Business management and point of sale for restaurants, bars, lounges, cafés, nightclubs, hotels, retail shops and supermarkets: POS with tables and orders, kitchen and bar screens, custom payment methods, receipts, inventory, expenses, accounting, staff roles and reports. Web app plus Windows, Mac and Android apps with one account; the Windows and Mac apps keep selling without internet and sync when the connection comes back.",
    "featureList": [
        "One LoungeOS account on the web, Windows, Mac and Android, with email and password or Continue with Google",
        "Setup wizard: business type, name, logo, currency, taxes, payment methods, opening hours and suggested categories",
        "Point of sale for touch and mouse on any screen size",
        "Tables and floors, split, move and merge bills, kitchen and bar screens",
        "QR code table ordering with staff approval",
        "Customer tabs (pay later) with balances and part payments",
        "Several branches with a copy of the menu, tables, settings and team",
        "Android phone app with role-based notifications and a home-screen widget",
        "Custom payment methods such as cash, MTN Mobile Money, Orange Money, card and bank transfer",
        "Receipts on 58 mm and 80 mm thermal printers, or PDF, with a print button on every order",
        "Inventory with stock movements, low-stock alerts and suppliers",
        "Expenses with your own categories",
        "Accounting with a chart of accounts and a journal",
        "Daily, weekly and monthly reports",
        "Staff roles, permissions, quick PIN on a shared till and an activity log",
        "Offline selling on the Windows and Mac apps with automatic sync",
        "Cloud copy of all data and daily full backups",
        "English and French interface",
    ],
    "screenshot": [SITE + "/images/screens/loungeos-pos-order-screen.webp",
                   SITE + "/images/screens/loungeos-kitchen-display-system.webp",
                   SITE + "/images/screens/loungeos-inventory-dashboard.webp"],
    "offers": plan_offers(),
}


def breadcrumb_node(url, crumbs):
    items = []
    for i, (name, u) in enumerate(crumbs, 1):
        items.append({"@type": "ListItem", "position": i, "name": html.unescape(name), "item": SITE + u})
    return {"@type": "BreadcrumbList", "@id": SITE + url + "#breadcrumb", "itemListElement": items}


# ---------------------------------------------------------------- shortcodes
def figures_of(p):
    """(image, alt) for each [[figure:...]] in a page's body."""
    return [(m.group(1).strip(), m.group(2).strip())
            for m in re.finditer(r"\[\[figure:([^|\]]+)\|([^|\]]+)", p.get("body_md", ""))]


def card_images(cards, used=()):
    """Choose a thumbnail per card so a row never shows the same screenshot twice,
    nor the screenshot already at the top of the page. A card falls back to one of
    its own page's figures, then to any screenshot not yet in the row."""
    used, out = set(used), []
    for p in cards:
        title = p.get("card_title") or p["h1"]
        options = [(p.get("image", "loungeos-pos-order-screen"), p.get("image_alt", title))] + figures_of(p)
        options += [(g, title) for g in CARD_FALLBACK_IMAGES]
        name, alt = next((o for o in options if o[0] not in used), options[0])
        used.add(name)
        out.append((name, alt))
    return out


CARD_FALLBACK_IMAGES = ["loungeos-pos-order-screen", "loungeos-kitchen-display-system", "loungeos-inventory-dashboard",
                        "loungeos-sales-reports", "loungeos-table-management", "loungeos-floor-management",
                        "loungeos-menu-management", "loungeos-order-management"]


def cards_html(cards, lang, used=()):
    return "\n".join(card_html(p, lang, img=im) for p, im in zip(cards, card_images(cards, used)))


def card_html(p, lang, cta=None, img=None):
    title = p.get("card_title") or p["h1"]
    desc = p.get("card_desc") or p["description"]
    tag = p.get("category") or p.get("label") or ""
    img, alt = img or (p.get("image", "loungeos-pos-order-screen"), p.get("image_alt", title))
    more = cta or (T[lang]["read_more"] if p["type"] == "blog" else T[lang]["learn_more"])
    return f"""<a class="post-card" href="{p['url']}">
  <img src="/images/screens/{img}-800.webp" width="800" height="430" alt="{esc(alt)}" loading="lazy" decoding="async" />
  <div class="post-card-body">
    <span class="tag">{esc(tag)}</span>
    <h3>{esc(title)}</h3>
    <p>{esc(desc)}</p>
    <span class="read-more">{more}</span>
  </div>
</a>"""


def cta_box(lang, title=None, text=None):
    t = T[lang]
    return f"""<div class="cta-box">
  <h2>{title or t['cta_title']}</h2>
  <p>{text or t['cta_text']}</p>
  <div class="cta-actions">
    <a class="btn btn-primary btn-lg" href="{SIGNUP}">{t['start_trial']}</a>
    <a class="btn btn-secondary btn-lg" href="{'/fr/telecharger/' if lang == 'fr' else '/download/'}">{t['cta_btn2']}</a>
  </div>
</div>"""


def shortcodes(md, page, by_url):
    lang = page["lang"]

    def fig(m):
        name, alt, *cap = m.group(1).split("|")
        cap = f"<figcaption>{cap[0].strip()}</figcaption>" if cap and cap[0].strip() else ""
        return f'<figure>{img_tag(name.strip(), alt.strip())}{cap}</figure>'

    def cards(m):
        urls = [u.strip() for u in m.group(1).split(",") if u.strip()]
        found = []
        for u in urls:
            if u not in by_url:
                if LENIENT:
                    continue
                raise SystemExit(f"{page['url']}: card link {u} not found")
            found.append(by_url[u])
        return '<div class="card-grid">\n' + cards_html(found, lang, [page.get("image")]) + "\n</div>"

    def phones(m):
        figs = []
        for part in m.group(1).split(";;"):
            name, alt, *cap = part.split("|")
            c = f"<figcaption>{cap[0].strip()}</figcaption>" if cap and cap[0].strip() else ""
            figs.append(f'<figure>{img_tag(name.strip(), alt.strip(), sizes="240px")}{c}</figure>')
        return '<div class="phone-row">' + "".join(figs) + "</div>"

    md = re.sub(r"\[\[phones:(.+?)\]\]", phones, md)
    md = re.sub(r"\[\[figure:(.+?)\]\]", fig, md)
    md = re.sub(r"\[\[cards:(.+?)\]\]", cards, md)
    md = md.replace("[[cta]]", cta_box(lang))
    md = re.sub(r"\[\[include:(\w+)\]\]", lambda m: INCLUDES[m.group(1)](lang), md)
    return md


def fr_number(v):
    """30,000 -> 30 000 with a narrow no-break space, as written in French."""
    return v.replace(",", "\u202f")


def money(amount, cur, lang):
    """US$10 / 6,000 FCFA in English, 10 $ US / 6 000 FCFA in French.
    Keep in sync with formatPrice() in /app.js so the price doesn't change on load."""
    n = f"{amount:,}"
    if lang == "fr":
        n = fr_number(n)
    if cur == "XAF":
        return f"{n}\u00a0FCFA"
    return f"{n}\u00a0$\u00a0US" if lang == "fr" else f"US${n}"


def plan_seats(users, devices, lang):
    """'2 users, 2 devices' / '2 utilisateurs, 2 appareils'."""
    if lang == "fr":
        u = "Utilisateurs illimités" if users is None else f"{users} utilisateurs"
        d = f"{devices[:-1]} appareils et plus" if devices.endswith("+") else f"{devices} appareils"
    else:
        u = "Unlimited users" if users is None else f"{users} users"
        d = f"{devices} devices"
    return f"{u}, {d}"


def price_table(lang):
    if lang == "fr":
        head = ("<tr><th>Formule</th><th>Mensuel ($ US)</th><th>Annuel ($ US)</th>"
                "<th>Mensuel (FCFA)</th><th>Annuel (FCFA)</th></tr>")
    else:
        head = ("<tr><th>Plan</th><th>Monthly (US$)</th><th>Yearly (US$)</th>"
                "<th>Monthly (FCFA)</th><th>Yearly (FCFA)</th></tr>")
    rows = []
    for _, name, _, _, usd_m, usd_y, xaf_m, xaf_y in PRICES:
        cells = [money(usd_m, "USD", lang), money(usd_y, "USD", lang),
                 money(xaf_m, "XAF", lang), money(xaf_y, "XAF", lang)]
        rows.append(f"<tr><td>{name}</td>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    return f"<table>\n<thead>{head}</thead>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>"


PLAN_FEATURES = {
    "en": {
        "starter": ["Point of sale (POS), tables, kitchen and bar screens", "Inventory and suppliers",
                    "Customer tabs (pay later)", "Receipts", "Daily reports"],
        "business": ["Everything in Starter", "Expenses and accounting", "Weekly and monthly reports",
                     "QR code table ordering", "Shifts and cash control (coming soon)"],
        "pro": ["Everything in Business", "Several branches", "All-branches sales overview",
                "Priority support", "Payroll (coming soon)"],
    },
    "fr": {
        "starter": ["Caisse, tables, écrans cuisine et bar", "Stocks et fournisseurs",
                    "Comptes clients (payer plus tard)", "Reçus", "Rapports journaliers"],
        "business": ["Tout ce que propose Starter", "Dépenses et comptabilité", "Rapports hebdomadaires et mensuels",
                     "Commande par QR code à table", "Services et contrôle de caisse (bientôt disponible)"],
        "pro": ["Tout ce que propose Business", "Plusieurs succursales", "Vue des ventes de toutes les succursales",
                "Support prioritaire", "Paie (bientôt disponible)"],
    },
}


def plan_cards(lang):
    """Starter, Business and Pro cards with a monthly/yearly switch. The static HTML
    shows US$ monthly prices; app.js switches to yearly on request and to FCFA for
    visitors in Cameroon. app.js reads data-plan and writes .price, .price-period and
    .price-savings, and the .billing-toggle state."""
    fr = lang == "fr"
    L = {
        "monthly": "Mensuel" if fr else "Monthly",
        "yearly": "Annuel" if fr else "Yearly",
        "free2": "2 mois offerts" if fr else "2 months free",
        "switch": "Payer à l'année (2 mois offerts)" if fr else "Pay yearly (2 months free)",
        "pm": "/ mois" if fr else "/ month",
        "popular": "Le plus choisi" if fr else "Most popular",
        "start": "Commencer l'essai gratuit" if fr else "Start free trial",
        "yousave": "Vous économisez" if fr else "You save",
        "note": (f"Chaque formule commence par un essai gratuit de {TRIAL_DAYS} jours avec les fonctionnalités "
                 "Business, sans paiement à l'avance. Les prix s'affichent en FCFA au Cameroun et en dollars US "
                 "partout ailleurs."
                 if fr else
                 f"Every plan starts with a {TRIAL_DAYS}-day free trial with Business features. No payment up "
                 "front. Visitors in Cameroon see prices in FCFA, everyone else in US$."),
    }

    def li(items):
        return "\n".join(f"<li>{CHECK} {i}</li>" for i in items)

    cards = []
    for key, name, users, devices, usd_m, usd_y, _, _ in PRICES:
        featured = key == "business"
        badge = f'\n    <span class="price-card-badge">{L["popular"]}</span>' if featured else ""
        btn = "btn-accent" if featured else "btn-primary"
        save = money(usd_m * 12 - usd_y, "USD", lang)
        features = [plan_seats(users, devices, lang)] + PLAN_FEATURES[lang][key]
        cards.append(f"""  <div class="price-card{' featured' if featured else ''}" data-plan="{key}">{badge}
    <h3>{name}</h3>
    <div class="price">{money(usd_m, "USD", lang)}</div>
    <div class="price-period">{L['pm']}</div>
    <div class="price-savings" hidden>{L['yousave']} {save}</div>
    <ul class="price-features">{li(features)}</ul>
    <a href="{SIGNUP}" class="btn {btn}">{L['start']}</a>
  </div>""")
    cards = "\n".join(cards)
    return f"""<div class="plans-breakout">
<div class="billing-toggle">
  <span class="active" data-billing="monthly">{L['monthly']}</span>
  <button type="button" class="toggle-switch" role="switch" aria-checked="false" aria-label="{L['switch']}"></button>
  <span data-billing="yearly">{L['yearly']}</span>
  <span class="yearly-badge">{L['free2']}</span>
</div>
<div class="pricing-grid pricing-grid-3" style="margin: 0 auto 1.5rem;">
{cards}
</div>
</div><p class="region-price-note">{L['note']}</p>"""

INCLUDES = {"price_table": price_table, "plans": plan_cards}


# ---------------------------------------------------------------- page build
MD_EXT = ["extra", "toc", "sane_lists", "smarty"]
MD_CFG = {"toc": {"permalink": False, "toc_depth": "2-3"},
          "smarty": {"smart_angled_quotes": False}}


def render_body(page, by_url):
    md_src = shortcodes(page["body_md"], page, by_url)
    body = markdown.markdown(md_src, extensions=MD_EXT, extension_configs=MD_CFG)
    soup = BeautifulSoup(body, "html.parser")
    # FAQ extraction
    faq = []
    faq_h2 = None
    for h2 in soup.find_all("h2"):
        if h2.get_text(strip=True).lower() in ("frequently asked questions", "questions fréquentes", "faq"):
            faq_h2 = h2
            break
    if page.get("faq_all"):
        q, parts = None, []
        for el in soup.find_all(recursive=False):
            if el.name == "h2":
                if q:
                    faq.append((q, parts))
                q, parts = None, []
            elif el.name == "h3":
                if q:
                    faq.append((q, parts))
                q, parts = el.get_text(" ", strip=True), []
            elif q and el.name in ("p", "ul", "ol", "table"):
                parts.append(str(el))
        if q:
            faq.append((q, parts))
        faq_h2 = None
    if faq_h2:
        q, parts = None, []
        for sib in faq_h2.find_next_siblings():
            if sib.name == "h2":
                break
            if sib.name == "h3":
                if q:
                    faq.append((q, parts))
                q, parts = sib.get_text(" ", strip=True), []
            elif q and sib.name in ("p", "ul", "ol", "table"):
                parts.append(str(sib))
        if q:
            faq.append((q, parts))
    for table in soup.find_all("table"):
        thead = table.find("thead")
        if thead and not thead.get_text(strip=True):
            thead.decompose()
        if not (table.parent and "table-wrap" in (table.parent.get("class") or [])):
            wrap = soup.new_tag("div", attrs={"class": "table-wrap", "tabindex": "0", "role": "region",
                                              "aria-label": "Table" if page["lang"] == "en" else "Tableau"})
            table.wrap(wrap)
    for ul in soup.find_all("ul"):
        items = ul.find_all("li", recursive=False)
        if items and all(li.get_text(strip=True).startswith("☐") for li in items):
            ul["class"] = (ul.get("class") or []) + ["checklist"]
    toc = [(h.get("id"), h.get_text(" ", strip=True)) for h in soup.find_all("h2")
           if h.get("id") and not h.find_parent(class_="cta-box")
           and not h.find_parent(class_="key-takeaways")]
    words = len(soup.get_text(" ").split())
    return str(soup), faq, toc, words


def faq_node(url, faq):
    ents = []
    for q, parts in faq:
        text = BeautifulSoup("".join(parts), "html.parser")
        for a in text.find_all("a"):
            href = a.get("href", "")
            if href.startswith("/"):
                a["href"] = SITE + href
        ans = re.sub(r"\s+", " ", str(text)).strip()
        ents.append({"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": ans}})
    return {"@type": "FAQPage", "@id": SITE + url + "#faq", "mainEntity": ents}


def crumbs_for(page, by_url):
    lang = page["lang"]
    home = ("Accueil", "/fr/") if lang == "fr" else ("Home", "/")
    trail = [home]
    for name, u in page.get("breadcrumb", []):
        trail.append((name, u))
    if page["url"] != home[1]:
        trail.append((page.get("crumb") or page.get("card_title") or page["h1"], page["url"]))
    return trail


def head_html(page, graph):
    lang = page["lang"]
    t = T[lang]
    url = SITE + page["url"]
    alts = ""
    if page["alternates"]:
        lines = [f'    <link rel="alternate" hreflang="{l}" href="{SITE}{u}" />'
                 for l, u in sorted(page["alternates"].items())]
        default = page["alternates"].get("en", page["url"])
        lines.append(f'    <link rel="alternate" hreflang="x-default" href="{SITE}{default}" />')
        alts = "\n".join(lines) + "\n"
    og_type = "article" if page["type"] == "blog" else "website"
    art = ""
    if page["type"] == "blog":
        art = (f'    <meta property="article:published_time" content="{page["published"]}" />\n'
               f'    <meta property="article:modified_time" content="{page["modified"]}" data-auto="modified" />\n'
               f'    <meta property="article:section" content="{esc(page.get("category", ""))}" />\n')
    og_title = page.get("og_title") or page["title"].split(" | ")[0]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    ld = ld.replace("</", "<\\/")
    no = page.get("noindex")
    robots = "noindex, follow" if no else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    return f"""<!doctype html>
<html lang="{lang}"{' data-no-autolang' if lang != 'en' else ''}>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(page['title'])}</title>
    <meta name="description" content="{esc(page['description'])}" />
    <meta name="robots" content="{robots}" />
    <link rel="canonical" href="{url}" />
{alts}    <meta property="og:type" content="{og_type}" />
    <meta property="og:site_name" content="LoungeOS" />
    <meta property="og:locale" content="{t['og_locale']}" />
    <meta property="og:title" content="{esc(og_title)}" />
    <meta property="og:description" content="{esc(page['description'])}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{SITE}/images/og-loungeos.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="LoungeOS: offline POS for restaurants, bars and lounges" />
{art}    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{esc(og_title)}" />
    <meta name="twitter:description" content="{esc(page['description'])}" />
    <meta name="twitter:image" content="{SITE}/images/og-loungeos.jpg" />

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/style.css" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="alternate" type="application/rss+xml" title="LoungeOS Blog" href="{SITE}/blog/feed.xml" />

    <script type="application/ld+json">
{ld}
    </script>
{ANALYTICS}
  </head>"""


def hero_html(page, crumbs, minutes=None):
    lang = page["lang"]
    t = T[lang]
    bc = []
    for i, (name, u) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            bc.append(f'<span aria-current="page">{name}</span>')
        else:
            bc.append(f'<a href="{u}">{name}</a>')
    bc = ' <span aria-hidden="true">›</span> '.join(bc)
    bc = f'<nav class="breadcrumbs" aria-label="Breadcrumb">{bc}</nav>' if len(crumbs) > 1 else ""
    label = f'<p class="section-label">{page.get("category") or page.get("label", "")}</p>' if (page.get("category") or page.get("label")) else ""
    lead = f'<p class="lead">{page["lead"]}</p>' if page.get("lead") else ""
    if page["type"] == "help":
        meta = (f'<div class="article-meta"><span>{t["help_for"]} LoungeOS {APP_VERSION}</span>'
                f'<span>{t["updated"]} <time datetime="{page["modified"]}" data-auto="modified">{fmt_date(page["modified"], lang)}</time></span>'
                f'<span>{minutes} {t["min_read"]}</span></div>')
        actions = ""
        media = ""
    elif page["type"] == "blog":
        meta = (f'<div class="article-meta"><span>{t["by"]} <a href="/about/">{t["team"]}</a></span>'
                f'<span>{t["published"]} <time datetime="{page["published"]}">{fmt_date(page["published"], lang)}</time></span>'
                f'<span>{t["updated"]} <time datetime="{page["modified"]}" data-auto="modified">{fmt_date(page["modified"], lang)}</time></span>'
                f'<span>{minutes} {t["min_read"]}</span></div>')
        actions = ""
        media = ""
    else:
        meta = ""
        sec_label, sec_url = page.get("hero_secondary") or (t["see_pricing"], "/fr/tarifs/" if lang == "fr" else "/pricing/")
        actions = f"""<div class="hero-actions">
          <a href="{SIGNUP}" class="btn btn-primary btn-lg">{t['start_trial']} {ARROW}</a>
          <a href="{sec_url}" class="btn btn-secondary btn-lg">{sec_label}</a>
        </div>
        <p class="trust-line">{t['trust']}</p>""" if not page.get("no_hero_cta") else ""
        media = ""
        if page.get("image") and not page.get("no_hero_image"):
            media = f'<div class="page-hero-media">{img_tag(page["image"], page.get("image_alt", page["h1"]), hero=True, sizes="(max-width: 1100px) 100vw, 1100px")}</div>'
    return f"""      <header class="page-hero">
        {bc}
        {label}
        <h1>{page['h1']}</h1>
        {lead}
        {meta}
        {actions}
        {media}
      </header>"""


FR_PUNCT = [
    (re.compile(r"[ \u00a0]([;!?])"), "\u202f\\1"),  # narrow no-break space before ; ! ?
    (re.compile(r"[ \u00a0]:(?=\s|$|<)"), "\u00a0:"),   # no-break space before a colon
    (re.compile(r"«[ \u00a0]"), "«\u00a0"),
    (re.compile(r"[ \u00a0]»"), "\u00a0»"),
]


def fr_typography(page_html):
    """Keep French punctuation attached to its word (« … », ?, !, :, ;) so it never
    wraps onto a line of its own. Touches the text of <body> only, never tags,
    attributes or scripts."""
    head, sep, body = page_html.partition("<body>")
    if not sep:
        return page_html
    out, in_script = [], False
    for chunk in re.split(r"(<[^>]+>)", body):
        if chunk.startswith("<"):
            low = chunk.lower()
            if low.startswith("<script") or low.startswith("<style"):
                in_script = True
            elif low.startswith("</script") or low.startswith("</style"):
                in_script = False
            out.append(chunk)
        elif in_script or not chunk.strip():
            out.append(chunk)
        else:
            for rx, sub in FR_PUNCT:
                chunk = rx.sub(sub, chunk)
            out.append(chunk)
    return head + sep + "".join(out)


def build_page(page, by_url, pages):
    lang = page["lang"]
    t = T[lang]
    body, faq, toc, words = render_body(page, by_url)
    minutes = max(3, math.ceil(words / 220))
    crumbs = crumbs_for(page, by_url)
    url = page["url"]

    graph = [ORG, WEBSITE]
    pnode_type = page.get("schema_type", "WebPage")
    pnode = {"@type": pnode_type, "@id": SITE + url + "#webpage", "url": SITE + url,
             "name": page["title"], "description": page["description"], "inLanguage": lang,
             "isPartOf": {"@id": WEBSITE_ID}, "breadcrumb": {"@id": SITE + url + "#breadcrumb"},
             "dateModified": page["modified"]}
    if page.get("image"):
        pnode["primaryImageOfPage"] = {"@type": "ImageObject",
                                       "url": f"{SITE}/images/screens/{page['image']}.webp"}
    if page["type"] in ("feature", "solution", "region", "core", "home-fr"):
        pnode["about"] = {"@id": SOFTWARE_ID}
        graph.append(SOFTWARE)
    graph.append(pnode)
    if page["type"] == "blog":
        img = f"{SITE}/images/screens/{page.get('image', 'loungeos-pos-order-screen')}.webp"
        art = {"@type": "BlogPosting", "@id": SITE + url + "#article", "headline": page["h1"],
               "description": page["description"], "image": [img, SITE + "/images/og-loungeos.jpg"],
               "datePublished": page["published"], "dateModified": page["modified"],
               "author": {"@type": "Organization", "@id": ORG_ID, "name": "LoungeOS", "url": SITE + "/about/"},
               "publisher": {"@id": ORG_ID}, "mainEntityOfPage": {"@id": SITE + url + "#webpage"},
               "inLanguage": lang, "articleSection": page.get("category", ""), "wordCount": words,
               "about": [{"@type": "Thing", "name": k} for k in page.get("about", [])],
               "mentions": {"@id": SOFTWARE_ID}}
        if not art["about"]:
            del art["about"]
        graph.append(art)
    if page["type"] == "help":
        graph.append({"@type": "TechArticle", "@id": SITE + url + "#article", "headline": page["h1"],
                      "description": page["description"], "inLanguage": lang,
                      "dateModified": page["modified"], "datePublished": page.get("published", page["modified"]),
                      "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
                      "mainEntityOfPage": {"@id": SITE + url + "#webpage"},
                      "image": f"{SITE}/images/screens/{page.get('image', 'loungeos-pos-order-screen')}.webp",
                      "about": {"@id": SOFTWARE_ID}, "proficiencyLevel": "Beginner"})
    graph.append(breadcrumb_node(url, crumbs))
    if faq:
        graph.append(faq_node(url, faq))

    parts = [head_html(page, graph), "  <body>", nav_html(lang), '    <main id="main-content">',
             hero_html(page, crumbs, minutes)]

    if page["type"] == "help":
        toc_html = ""
        if len(toc) >= 3:
            lis = "\n".join(f'<li><a href="#{i}">{esc(x)}</a></li>' for i, x in toc)
            toc_html = f'<details class="toc" open><summary>{t["help_toc"]}</summary><ul>\n{lis}\n</ul></details>'
        back = "/fr/aide/" if lang == "fr" else "/help/"
        parts.append(f"""      <article class="content-section">
        <div class="prose">
{toc_html}
{body}
<p class="help-steps-note">{t["help_stuck"]}</p>
<p><a href="{back}">← {t["help_back"]}</a></p>
        </div>
      </article>""")
    elif page["type"] == "blog":
        tk = ""
        if page.get("takeaways"):
            lis = "\n".join(f"<li>{markdown.markdown(x)[3:-4]}</li>" for x in page["takeaways"])
            tk = f'<aside class="key-takeaways"><h2>{t["takeaways"]}</h2><ul>\n{lis}\n</ul></aside>'
        toc_html = ""
        toc_items = [x for x in toc if x[1].lower() not in (t["faq_heading"].lower(),)]
        if len(toc) >= 3:
            lis = "\n".join(f'<li><a href="#{i}">{esc(x)}</a></li>' for i, x in toc)
            # Headings that already carry "1. ", "2. " get a plain list, not a second number
            lst = "ul" if any(re.match(r"\d+[.)]\s", x) for _, x in toc) else "ol"
            toc_html = f'<details class="toc" open><summary>{t["toc"]}</summary><{lst}>\n{lis}\n</{lst}></details>'
        fig = ""
        if page.get("image"):
            fig = f'<figure>{img_tag(page["image"], page.get("image_alt", page["h1"]), hero=True, sizes="(max-width: 800px) 100vw, 760px")}</figure>'
        article = f"""      <article class="content-section">
        <div class="prose">
{fig}
{tk}
{toc_html}
{body}
{"" if "[[cta]]" in page["body_md"] else cta_box(lang)}
        </div>
      </article>"""
        parts.append(article)
    else:
        parts.append(f"""      <section class="content-section">
        <div class="prose prose-wide">
{body}
        </div>
      </section>""")
        if not page.get("no_cta"):
            parts.append(f'      <section style="padding: 0 1.5rem 1rem">{cta_box(lang)}</section>')

    rel = page.get("related", [])
    if rel:
        cards = cards_html([by_url[u] for u in rel if u in by_url or not LENIENT], lang, [page.get("image")])
        heading = t["related"] if page["type"] in ("blog", "help") else t["explore"]
        parts.append(f"""      <section class="related-section">
        <h2 class="section-title">{heading}</h2>
        <div class="card-grid">
{cards}
        </div>
      </section>""")

    parts += ["    </main>", footer_html(lang), tail_scripts(lang), "  </body>", "</html>", ""]
    out = "\n".join(parts)
    return (fr_typography(out) if lang == "fr" else out), words


HELP_SECTIONS = {
    "en": ["Get started", "Selling", "Products and stock", "Money and reports", "Team and branches", "Account, data and troubleshooting"],
    "fr": ["Bien démarrer", "Vendre", "Produits et stocks", "Argent et rapports", "Équipe et succursales", "Compte, données et dépannage"],
}


def help_index(pages, by_url, lang):
    url = "/fr/aide/" if lang == "fr" else "/help/"
    other = "/help/" if lang == "fr" else "/fr/aide/"
    arts = sorted([p for p in pages if p["type"] == "help" and p["lang"] == lang],
                  key=lambda p: (HELP_SECTIONS[lang].index(p["section"]), p.get("order", 99), p["url"]))
    t = T[lang]
    sections = []
    for sec in HELP_SECTIONS[lang]:
        row = [p for p in arts if p["section"] == sec]
        if not row:
            continue
        links = "\n".join(f'<a class="help-link" href="{p["url"]}"><strong>{esc(p.get("card_title") or p["h1"])}</strong>'
                          f'<span>{esc(p.get("card_desc") or p["description"])}</span></a>' for p in row)
        sections.append(f'<h2 class="blog-section-title">{esc(sec)}</h2>\n<div class="help-grid">\n{links}\n</div>')
    fr = lang == "fr"
    page = {
        "url": url, "lang": lang, "type": "help-index", "alternates": {"en": "/help/", "fr": "/fr/aide/"},
        "title": ("Centre d'aide LoungeOS : guides pas à pas avec captures" if fr else
                  "LoungeOS Help Centre: Step-by-Step Guides with Screenshots"),
        "description": ("Guides pas à pas pour LoungeOS 2.1 : installation, caisse, cuisine et bar, commande par QR code, stocks, dépenses, comptabilité, succursales et application mobile."
                        if fr else
                        "Step-by-step LoungeOS 2.1 guides with screenshots: setup, the till, kitchen and bar, QR table ordering, stock, expenses, accounting, branches and the phone app."),
        "h1": "Centre d'aide LoungeOS" if fr else "LoungeOS Help Centre",
        "lead": ("Chaque guide suit l'application telle qu'elle est aujourd'hui (version " + APP_VERSION + "), avec des captures de l'établissement de démonstration Viona Lounge à Buea. Les chiffres et les noms du personnel sont des exemples."
                 if fr else
                 "Every guide follows the app as it is today (version " + APP_VERSION + "), with screenshots from the sample business Viona Lounge in Buea. Figures and staff names are sample data."),
        "label": t["help"], "modified": max(p["modified"] for p in arts), "no_hero_cta": True,
    }
    crumbs = [(t["home"], "/fr/" if fr else "/"), (t["help"], url)]
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + p["url"], "name": p["h1"]} for i, p in enumerate(arts)]
    graph = [ORG, WEBSITE,
             {"@type": ["WebPage", "CollectionPage"], "@id": SITE + url + "#webpage", "url": SITE + url,
              "name": page["title"], "description": page["description"], "inLanguage": lang,
              "isPartOf": {"@id": WEBSITE_ID}, "breadcrumb": {"@id": SITE + url + "#breadcrumb"},
              "dateModified": page["modified"], "about": {"@id": SOFTWARE_ID},
              "mainEntity": {"@type": "ItemList", "itemListElement": items}},
             SOFTWARE, breadcrumb_node(url, crumbs)]
    search = ("Rechercher dans l'aide" if fr else "Search the help centre")
    box = (f'<div class="help-search"><input type="search" id="helpSearch" placeholder="{search}…" aria-label="{search}" /></div>'
           '<script>(function(){var i=document.getElementById("helpSearch");if(!i)return;i.addEventListener("input",function(){var q=i.value.toLowerCase().trim();'
           'document.querySelectorAll(".help-link").forEach(function(a){a.style.display=!q||a.textContent.toLowerCase().indexOf(q)>-1?"":"none";});});})();</script>')
    out = [head_html(page, graph), "  <body>", nav_html(lang), '    <main id="main-content">',
           hero_html(page, crumbs),
           '      <section class="content-section" style="max-width: 1100px; margin: 0 auto;">', box,
           "\n".join(sections), "      </section>",
           f'      <section style="padding: 2rem 1.5rem 1rem">{cta_box(lang)}</section>',
           "    </main>", footer_html(lang), tail_scripts(lang), "  </body>", "</html>", ""]
    html_out = "\n".join(out)
    return url, (fr_typography(html_out) if fr else html_out)


def blog_index(pages, by_url):
    posts = sorted([p for p in pages if p["type"] == "blog"],
                   key=lambda p: (p["published"], p["url"]), reverse=True)
    order = ["POS buying guides", "Loss prevention", "Operations", "Inventory & finance", "Africa", "En français"]
    def section(p):
        return "En français" if p["lang"] == "fr" else p["category"]
    cats = sorted({section(p) for p in posts}, key=lambda c: order.index(c) if c in order else len(order))
    sections = []
    for c in cats:
        row = [p for p in posts if section(p) == c]
        cards = "\n".join(card_html(p, p["lang"], img=im) for p, im in zip(row, card_images(row)))
        sections.append(f'<h2 class="blog-section-title">{esc(c)}</h2>\n<div class="card-grid">\n{cards}\n</div>')
    page = {
        "url": "/blog/", "lang": "en", "type": "blog-index", "alternates": {},
        "title": "LoungeOS Blog: Restaurant, Bar & Lounge Management Guides",
        "description": "Practical guides on restaurant POS systems, offline operations, theft prevention, inventory, food cost, kitchen display systems, mobile money and running hospitality businesses in Africa.",
        "h1": "Guides for running a tighter restaurant, bar or lounge",
        "lead": "Practical, numbers-first guides on POS systems, loss prevention, inventory, accounting and running service when the power or internet goes down.",
        "label": "LoungeOS Blog", "modified": max(p["modified"] for p in posts),
        "no_hero_cta": True,
    }
    crumbs = [("Home", "/"), ("Blog", "/blog/")]
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + p["url"], "name": p["h1"]}
             for i, p in enumerate(posts)]
    graph = [ORG, WEBSITE,
             {"@type": ["WebPage", "CollectionPage"], "@id": SITE + "/blog/#webpage", "url": SITE + "/blog/",
              "name": page["title"], "description": page["description"], "inLanguage": "en",
              "isPartOf": {"@id": WEBSITE_ID}, "breadcrumb": {"@id": SITE + "/blog/#breadcrumb"},
              "dateModified": page["modified"],
              "mainEntity": {"@type": "ItemList", "itemListElement": items}},
             breadcrumb_node("/blog/", crumbs)]
    out = [head_html(page, graph), "  <body>", nav_html("en"), '    <main id="main-content">',
           hero_html(page, crumbs),
           '      <section class="content-section" style="max-width: 1248px; margin: 0 auto;">',
           "\n".join(sections), "      </section>",
           f'      <section style="padding: 2rem 1.5rem 1rem">{cta_box("en")}</section>',
           "    </main>", footer_html("en"), tail_scripts("en"), "  </body>", "</html>", ""]
    return "\n".join(out)


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, "..", ".."))
    pages, by_url = load_pages()
    report = []
    for p in pages:
        html_out, words = build_page(p, by_url, pages)
        html_out = social_tags(version_links(html_out, repo), repo)
        path = os.path.join(repo, p["output"]) if p.get("output") else os.path.join(repo, p["url"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(html_out)
        report.append((p["url"], p["lang"], p["type"], words, len(p["title"]), len(p["description"])))
    if any(p["type"] == "blog" for p in pages):
        path = os.path.join(repo, "blog", "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(social_tags(version_links(blog_index(pages, by_url), repo), repo))
    if any(p["type"] == "help" for p in pages):
        for lang in ("en", "fr"):
            if not any(p["type"] == "help" and p["lang"] == lang for p in pages):
                continue
            url, out = help_index(pages, by_url, lang)
            path = os.path.join(repo, url.strip("/"), "index.html")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(social_tags(version_links(out, repo), repo))
    for r in sorted(report):
        flag = ""
        if r[4] > 65:
            flag += " TITLE>65"
        if not 110 <= r[5] <= 165:
            flag += f" DESC={r[5]}"
        print(f"{r[0]:55} {r[1]} {r[2]:8} {r[3]:5}w{flag}")
    print(len(report), "pages")


if __name__ == "__main__":
    main()

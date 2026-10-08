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
CONTENT = os.path.join(HERE, "content")
SITE = "https://loungeos.app"
TODAY = dt.date(2026, 10, 8)
SIGNUP = "https://account.loungeos.app/sign-up"
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
        "home": "Home", "blog": "Blog", "start_trial": "Start Free Trial",
        "see_pricing": "See pricing",
        "trust": "30-day free trial · No credit card · Works without internet",
        "by": "By", "team": "LoungeOS Team", "published": "Published",
        "updated": "Updated", "min_read": "min read", "takeaways": "Key takeaways",
        "toc": "In this guide", "related": "Keep reading", "explore": "Explore more",
        "cta_title": "Run your next service on LoungeOS",
        "cta_text": "Install LoungeOS on a Windows computer, connect your tablets and phones over Wi-Fi, and run real service for 30 days. Free, no credit card.",
        "cta_btn2": "Download for Windows",
        "read_more": "Read guide →", "learn_more": "Learn more →",
        "faq_heading": "Frequently asked questions",
        "og_locale": "en_US",
    },
    "fr": {
        "home": "Accueil", "blog": "Blog", "start_trial": "Essai gratuit",
        "see_pricing": "Voir les tarifs",
        "trust": "Essai gratuit de 30 jours · Sans carte bancaire · Fonctionne sans internet",
        "by": "Par", "team": "l'équipe LoungeOS", "published": "Publié le",
        "updated": "Mis à jour le", "min_read": "min de lecture", "takeaways": "Points clés",
        "toc": "Dans ce guide", "related": "À lire aussi", "explore": "Découvrir aussi",
        "cta_title": "Faites votre prochain service avec LoungeOS",
        "cta_text": "Installez LoungeOS sur un ordinateur Windows, connectez vos tablettes et téléphones en Wi-Fi et travaillez en conditions réelles pendant 30 jours. Gratuit, sans carte bancaire.",
        "cta_btn2": "Télécharger pour Windows",
        "read_more": "Lire le guide →", "learn_more": "En savoir plus →",
        "faq_heading": "Questions fréquentes",
        "og_locale": "fr_FR",
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
def img_tag(name, alt, hero=False, sizes="(max-width: 800px) 100vw, 960px"):
    attrs = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return (f'<img src="/images/screens/{name}.webp" '
            f'srcset="/images/screens/{name}-800.webp 800w, /images/screens/{name}.webp 1600w" '
            f'sizes="{sizes}" width="1600" height="861" alt="{esc(alt)}" {attrs} decoding="async" />')


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
        "badge": "Restaurant POS",
        "links": [("Home", "/"), ("Features", "/features/")],
        "solutions": ("Solutions", [("Restaurants", "/restaurant-pos/"), ("Bars", "/bar-pos/"),
                                    ("Lounges", "/lounge-pos/"), ("Nightclubs", "/nightclub-pos/"),
                                    ("Hotels", "/hotel-pos/"), ("Cafés &amp; Fast Food", "/cafe-pos/"),
                                    ("Cameroon", "/cameroon/"), ("Africa", "/africa/")]),
        "after": [("Pricing", "/pricing/"), ("Download", "/download/")],
        "resources": ("Resources", [("Blog", "/blog/"), ("FAQ", "/faq/"),
                                    ("Knowledge Base", "/knowledgebase.html"),
                                    ("Documentation", "/documentation.html"),
                                    ("About", "/about/"), ("Contact", "/contact/"),
                                    ("Français", "/fr/")]),
        "cta": "Start Free Trial",
    },
    "fr": {
        "badge": "Logiciel de caisse",
        "links": [("Accueil", "/fr/"), ("Fonctionnalités", "/fr/fonctionnalites/")],
        "solutions": ("Solutions", [("Restaurants", "/fr/logiciel-caisse-restaurant/"),
                                    ("Bars, lounges &amp; boîtes de nuit", "/fr/logiciel-gestion-bar-lounge/"),
                                    ("Hôtels", "/hotel-pos/"),
                                    ("Cameroun", "/fr/cameroun/"),
                                    ("Côte d'Ivoire", "/fr/cote-divoire/"),
                                    ("Sénégal", "/fr/senegal/"),
                                    ("Afrique francophone", "/fr/afrique/")]),
        "after": [("Tarifs", "/fr/tarifs/"), ("Télécharger", "/fr/telecharger/")],
        "resources": ("Ressources", [("Blog", "/blog/"), ("FAQ", "/fr/faq/"),
                                     ("Base de connaissances", "/knowledgebase.html"),
                                     ("Documentation", "/documentation.html"),
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
        "tagline": "Offline-first POS and management system for restaurants, bars, lounges and hotels. Built in Cameroon, used across Africa and beyond.",
        "chips": ["All currencies", "English &amp; French", "Works offline"],
        "cols": [
            ("Product", [("Features", "/features/"), ("Pricing", "/pricing/"), ("Download", "/download/"),
                         ("Offline POS", "/features/offline-pos/"),
                         ("Kitchen Display System", "/features/kitchen-display-system/"),
                         ("Inventory", "/features/inventory-management/"),
                         ("Accounting", "/features/restaurant-accounting/")]),
            ("Solutions", [("Restaurant POS", "/restaurant-pos/"), ("Bar POS", "/bar-pos/"),
                           ("Lounge POS", "/lounge-pos/"), ("Nightclub POS", "/nightclub-pos/"),
                           ("Hotel POS", "/hotel-pos/"), ("Café &amp; Fast Food POS", "/cafe-pos/")]),
            ("Countries", [("Cameroon", "/cameroon/"), ("Nigeria", "/nigeria/"), ("Ghana", "/ghana/"),
                           ("South Africa", "/south-africa/"), ("Africa", "/africa/"),
                           ("Cameroun (FR)", "/fr/cameroun/"), ("Côte d'Ivoire (FR)", "/fr/cote-divoire/"),
                           ("Sénégal (FR)", "/fr/senegal/")]),
            ("Resources", [("Blog", "/blog/"), ("FAQ", "/faq/"), ("Knowledge Base", "/knowledgebase.html"),
                           ("Documentation", "/documentation.html"), ("About", "/about/"),
                           ("Contact", "/contact/"), ("Privacy Policy", "/privacy.html"),
                           ("Terms of Service", "/terms.html"), ("Accessibility", "/accessibility.html"),
                           ("Legal", "/legal.html")]),
        ],
        "rights": "All rights reserved.",
        "cta": "Start Free Trial",
    },
    "fr": {
        "tagline": "Logiciel de caisse et de gestion hors ligne pour restaurants, bars, lounges et hôtels. Conçu au Cameroun, utilisé en Afrique et au-delà.",
        "chips": ["Toutes devises", "Français &amp; anglais", "Fonctionne hors ligne"],
        "cols": [
            ("Produit", [("Fonctionnalités", "/fr/fonctionnalites/"), ("Tarifs", "/fr/tarifs/"),
                         ("Télécharger", "/fr/telecharger/"), ("FAQ", "/fr/faq/")]),
            ("Solutions", [("Logiciel de caisse restaurant", "/fr/logiciel-caisse-restaurant/"),
                           ("Logiciel bar &amp; lounge", "/fr/logiciel-gestion-bar-lounge/"),
                           ("Afrique francophone", "/fr/afrique/")]),
            ("Pays", [("Cameroun", "/fr/cameroun/"), ("Côte d'Ivoire", "/fr/cote-divoire/"),
                      ("Sénégal", "/fr/senegal/"), ("Cameroon (EN)", "/cameroon/"),
                      ("Nigeria (EN)", "/nigeria/"), ("Ghana (EN)", "/ghana/")]),
            ("Ressources", [("Blog", "/blog/"), ("Base de connaissances", "/knowledgebase.html"),
                            ("Documentation", "/documentation.html"), ("À propos", "/about/"),
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
            <a href="mailto:hello@loungeos.app">hello@loungeos.app</a><br />
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
    <script defer src="/app.js"></script>
    <!-- Botpress Webchat -->
    <script defer src="https://cdn.botpress.cloud/webchat/v3.6/inject.js"></script>
    <script defer src="https://files.bpcontent.cloud/2026/06/19/19/20260619193215-LONFMDIT.js"></script>"""


# ---------------------------------------------------------------- schema
ORG = {
    "@type": "Organization",
    "@id": ORG_ID,
    "name": "LoungeOS",
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/images/logo/loungeos-icon-512.png", "width": 512, "height": 512},
    "image": SITE + "/images/og-loungeos.jpg",
    "description": "LoungeOS develops offline-first point of sale (POS) and management software for restaurants, bars, lounges, nightclubs and hotels.",
    "email": "hello@loungeos.app",
    "telephone": "+237679690703",
    "address": {"@type": "PostalAddress", "addressCountry": "CM"},
    "areaServed": ["CM", "Africa", "Worldwide"],
    "knowsLanguage": ["en", "fr"],
    "contactPoint": [
        {"@type": "ContactPoint", "contactType": "customer support", "email": "support@loungeos.app",
         "telephone": "+237679690703", "availableLanguage": ["English", "French"]},
        {"@type": "ContactPoint", "contactType": "sales", "email": "hello@loungeos.app",
         "telephone": "+237689699688", "availableLanguage": ["English", "French"]},
        {"@type": "ContactPoint", "contactType": "billing support", "email": "billing@loungeos.app"},
    ],
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


SOFTWARE = {
    "@type": "SoftwareApplication",
    "@id": SOFTWARE_ID,
    "name": "LoungeOS",
    "applicationCategory": "BusinessApplication",
    "applicationSubCategory": "Restaurant point of sale (POS) and management software",
    "operatingSystem": "Windows 10, Windows 11 (host computer); any modern web browser on the local network for tablets and phones",
    "softwareVersion": "1.3.6",
    "fileSize": "383MB",
    "downloadUrl": SITE + "/download/",
    "installUrl": SITE + "/download/",
    "url": SITE + "/",
    "inLanguage": ["en", "fr"],
    "publisher": {"@id": ORG_ID},
    "description": "Offline-first restaurant, bar and lounge POS with kitchen and bar display screens, table and floor management, inventory, role-based permissions with audit logs, and double-entry accounting. Runs on your own Windows computer and local Wi-Fi network without internet.",
    "featureList": [
        "Works without internet on the local network",
        "Point of sale with table and floor management",
        "Kitchen Display System (KDS) and Bar Display System (BDS) with automatic food/drink routing",
        "Split and merge bills; split payments across cash, card and mobile money",
        "Mobile money payment recording (MTN Mobile Money, Orange Money)",
        "Inventory and stock movements with low-stock alerts, suppliers and CSV import/export",
        "Role-based permissions for 8 roles and a searchable activity log",
        "Double-entry accounting: journals, profit & loss, balance sheet, cash flow",
        "Multi-currency (XAF, USD, EUR, GBP, NGN, GHS and custom) and multiple tax rates",
        "Thermal receipt printing with logo and custom messages",
        "Encrypted database backups and restore",
        "English and French interface",
    ],
    "screenshot": [SITE + "/images/screens/loungeos-pos-order-screen.webp",
                   SITE + "/images/screens/loungeos-kitchen-display-system.webp",
                   SITE + "/images/screens/loungeos-inventory-dashboard.webp"],
    "offers": [
        offer("30-day free trial", 0, "XAF"),
        offer("Monthly plan (FCFA zone)", 30000, "XAF", 1),
        offer("6-month plan (FCFA zone)", 150000, "XAF", 6),
        offer("12-month plan (FCFA zone)", 240000, "XAF", 12),
        offer("Monthly plan (international)", 49, "USD", 1),
        offer("12-month plan (international)", 468, "USD", 12),
    ],
}


def breadcrumb_node(url, crumbs):
    items = []
    for i, (name, u) in enumerate(crumbs, 1):
        items.append({"@type": "ListItem", "position": i, "name": html.unescape(name), "item": SITE + u})
    return {"@type": "BreadcrumbList", "@id": SITE + url + "#breadcrumb", "itemListElement": items}


# ---------------------------------------------------------------- shortcodes
def card_html(p, lang, cta=None):
    title = p.get("card_title") or p["h1"]
    desc = p.get("card_desc") or p["description"]
    tag = p.get("category") or p.get("label") or ""
    img = p.get("image", "loungeos-pos-order-screen")
    alt = p.get("image_alt", title)
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
        out = []
        for u in urls:
            if u not in by_url:
                if LENIENT:
                    continue
                raise SystemExit(f"{page['url']}: card link {u} not found")
            out.append(card_html(by_url[u], lang))
        return '<div class="card-grid">\n' + "\n".join(out) + "\n</div>"

    md = re.sub(r"\[\[figure:(.+?)\]\]", fig, md)
    md = re.sub(r"\[\[cards:(.+?)\]\]", cards, md)
    md = md.replace("[[cta]]", cta_box(lang))
    md = re.sub(r"\[\[include:(\w+)\]\]", lambda m: INCLUDES[m.group(1)](lang), md)
    return md


# Regional price table (keep in sync with REGIONAL_PRICING in app.js)
PRICES = [
    # region, currency label, monthly, 6-month per month, 6-month total, yearly per month, yearly total
    ("Cameroon, CEMAC &amp; UEMOA (FCFA zone)", "FCFA", "30,000", "25,000", "150,000", "20,000", "240,000"),
    ("Nigeria", "₦", "35,000", "30,000", "180,000", "25,000", "300,000"),
    ("Ghana", "GH₵", "299", "249", "1,494", "199", "2,388"),
    ("South Africa", "R", "599", "499", "2,994", "449", "5,388"),
    ("Other African &amp; emerging markets", "US$ (shown in local currency)", "25", "21", "126", "17", "204"),
    ("Europe / Eurozone", "€", "45", "40", "240", "35", "420"),
    ("United Kingdom", "£", "39", "35", "210", "31", "372"),
    ("United States, Canada, Gulf &amp; rest of world", "US$", "49", "44", "264", "39", "468"),
]
PRICES_FR_REGION = {
    "Cameroon, CEMAC &amp; UEMOA (FCFA zone)": "Cameroun, CEMAC &amp; UEMOA (zone FCFA)",
    "Other African &amp; emerging markets": "Autres pays africains &amp; émergents",
    "Europe / Eurozone": "Europe / zone euro",
    "United Kingdom": "Royaume-Uni",
    "United States, Canada, Gulf &amp; rest of world": "États-Unis, Canada, Golfe &amp; reste du monde",
    "South Africa": "Afrique du Sud",
}


def price_table(lang):
    if lang == "fr":
        head = ("<tr><th>Région</th><th>Devise</th><th>Mensuel</th><th>6 mois (par mois)</th>"
                "<th>12 mois (par mois)</th></tr>")
    else:
        head = ("<tr><th>Region</th><th>Currency</th><th>Monthly</th><th>6 months (per month)</th>"
                "<th>12 months (per month)</th></tr>")
    rows = []
    for region, cur, mo, s, st, y, yt in PRICES:
        r = PRICES_FR_REGION.get(region, region) if lang == "fr" else region
        tot = "total" if lang == "en" else "au total"
        rows.append(f"<tr><td>{r}</td><td>{cur}</td><td>{mo}</td><td>{s} ({st} {tot})</td>"
                    f"<td>{y} ({yt} {tot})</td></tr>")
    return f"<table>\n<thead>{head}</thead>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>"


def plan_cards(lang):
    fr = lang == "fr"
    L = {
        "trial": "Essai gratuit" if fr else "Free Trial",
        "free": "Gratuit" if fr else "Free",
        "for30": "pendant 30 jours" if fr else "for 30 days",
        "monthly": "Mensuel" if fr else "Monthly",
        "six": "Formule 6 mois" if fr else "6-Month Plan",
        "year": "Formule annuelle" if fr else "Yearly Plan",
        "pm": "/ mois" if fr else "/ month",
        "popular": "Le plus choisi" if fr else "Most Popular",
        "best": "Meilleure offre" if fr else "Best Value",
        "start": "Commencer l'essai" if fr else "Start Free Trial",
        "get": "Choisir" if fr else "Get Started",
        "all": "Toutes les fonctionnalités" if fr else "All features included",
        "unl": "Terminaux illimités" if fr else "Unlimited terminals",
        "kds": "Écrans cuisine &amp; bar (KDS/BDS)" if fr else "Kitchen &amp; bar display screens",
        "inv": "Stocks, comptabilité &amp; rapports" if fr else "Inventory, accounting &amp; reports",
        "nocard": "Sans carte bancaire" if fr else "No credit card required",
        "cancel": "Résiliable à tout moment" if fr else "Cancel anytime",
        "updates": "Mises à jour incluses" if fr else "Free software updates",
        "prio": "Support prioritaire" if fr else "Priority support",
        "total": "au total" if fr else "total",
        "save6": "1 mois offert" if fr else "1 month free",
        "save12": "4 mois offerts" if fr else "4 months free",
        "yousave": "Vous économisez" if fr else "You save",
    }

    def li(items):
        return "\n".join(f"<li>{CHECK} {i}</li>" for i in items)

    return f"""<div class="plans-breakout"><div class="pricing-grid pricing-grid-5" style="margin: 0 0 1.5rem;">
  <div class="price-card">
    <h3>{L['trial']}</h3>
    <div class="price">{L['free']}</div>
    <div class="price-period">{L['for30']}</div>
    <ul class="price-features">{li([L['all'], L['unl'], L['kds'], L['nocard']])}</ul>
    <a href="{SIGNUP}" class="btn btn-secondary">{L['start']}</a>
  </div>
  <div class="price-card">
    <h3>{L['monthly']}</h3>
    <div class="price" data-base-price="30000" data-plan="monthly">30 000 FCFA</div>
    <div class="price-period">{L['pm']}</div>
    <ul class="price-features">{li([L['all'], L['unl'], L['inv'], L['cancel']])}</ul>
    <a href="https://account.loungeos.app/checkout?duration=30" class="btn btn-secondary" data-checkout="30">{L['get']}</a>
  </div>
  <div class="price-card featured">
    <span class="price-card-badge">{L['popular']}</span>
    <h3>{L['six']}</h3>
    <div class="price" data-base-price="25000" data-plan="six">25 000 FCFA</div>
    <div class="price-period">{L['pm']}</div>
    <div class="price-total" data-base-total="150000" data-plan="six" data-total-label="{L['total']}">150 000 FCFA {L['total']}</div>
    <div class="price-savings" data-base-savings="30000" data-plan="six" data-free-months="{L['save6']}" data-save-label="{L['yousave']}">{L['yousave']} 30 000 FCFA ({L['save6']})</div>
    <ul class="price-features">{li([L['all'], L['unl'], L['inv'], L['updates']])}</ul>
    <a href="https://account.loungeos.app/checkout?duration=180" class="btn btn-primary" data-checkout="180">{L['get']}</a>
  </div>
  <div class="price-card">
    <span class="price-card-badge">{L['best']}</span>
    <h3>{L['year']}</h3>
    <div class="price" data-base-price="20000" data-plan="yearly">20 000 FCFA</div>
    <div class="price-period">{L['pm']}</div>
    <div class="price-total" data-base-total="240000" data-plan="yearly" data-total-label="{L['total']}">240 000 FCFA {L['total']}</div>
    <div class="price-savings" data-base-savings="120000" data-plan="yearly" data-free-months="{L['save12']}" data-save-label="{L['yousave']}">{L['yousave']} 120 000 FCFA ({L['save12']})</div>
    <ul class="price-features">{li([L['all'], L['unl'], L['inv'], L['prio']])}</ul>
    <a href="https://account.loungeos.app/checkout?duration=365" class="btn btn-secondary" data-checkout="365">{L['get']}</a>
  </div>
  <div class="price-card">
    <h3>Enterprise</h3>
    <div class="price">{'Sur devis' if fr else 'Custom'}</div>
    <div class="price-period">{'multi-sites &amp; grands comptes' if fr else 'multi-site &amp; groups'}</div>
    <ul class="price-features">{li(['Installation &amp; formation sur site' if fr else 'On-site setup &amp; training', 'Interlocuteur dédié' if fr else 'Dedicated account manager', 'Intégrations sur mesure' if fr else 'Custom integrations'])}</ul>
    <a href="mailto:hello@loungeos.app" class="btn btn-secondary">{'Contacter les ventes' if fr else 'Contact Sales'}</a>
  </div>
</div>
</div><p class="region-price-note" data-region-note>{'Les prix s’affichent automatiquement dans votre devise selon votre pays.' if fr else 'Prices are shown automatically in your local currency based on your country.'}</p>"""


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
    label = f'<p class="section-label">{page.get("category") or page.get("label", "")}</p>' if (page.get("category") or page.get("label")) else ""
    lead = f'<p class="lead">{page["lead"]}</p>' if page.get("lead") else ""
    if page["type"] == "blog":
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
        <nav class="breadcrumbs" aria-label="Breadcrumb">{bc}</nav>
        {label}
        <h1>{page['h1']}</h1>
        {lead}
        {meta}
        {actions}
        {media}
      </header>"""


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
    graph.append(breadcrumb_node(url, crumbs))
    if faq:
        graph.append(faq_node(url, faq))

    parts = [head_html(page, graph), "  <body>", nav_html(lang), '    <main id="main-content">',
             hero_html(page, crumbs, minutes)]

    if page["type"] == "blog":
        tk = ""
        if page.get("takeaways"):
            lis = "\n".join(f"<li>{markdown.markdown(x)[3:-4]}</li>" for x in page["takeaways"])
            tk = f'<aside class="key-takeaways"><h2>{t["takeaways"]}</h2><ul>\n{lis}\n</ul></aside>'
        toc_html = ""
        toc_items = [x for x in toc if x[1].lower() not in (t["faq_heading"].lower(),)]
        if len(toc) >= 3:
            lis = "\n".join(f'<li><a href="#{i}">{esc(x)}</a></li>' for i, x in toc)
            toc_html = f'<details class="toc" open><summary>{t["toc"]}</summary><ol>\n{lis}\n</ol></details>'
        fig = ""
        if page.get("image"):
            fig = f'<figure>{img_tag(page["image"], page.get("image_alt", page["h1"]), hero=True, sizes="(max-width: 800px) 100vw, 760px")}</figure>'
        article = f"""      <article class="content-section">
        <div class="prose">
{fig}
{tk}
{toc_html}
{body}
{cta_box(lang)}
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
        cards = "\n".join(card_html(by_url[u], lang) for u in rel if u in by_url or not LENIENT)
        heading = t["related"] if page["type"] == "blog" else t["explore"]
        parts.append(f"""      <section class="related-section">
        <h2 class="section-title">{heading}</h2>
        <div class="card-grid">
{cards}
        </div>
      </section>""")

    parts += ["    </main>", footer_html(lang), tail_scripts(lang), "  </body>", "</html>", ""]
    return "\n".join(parts), words


def blog_index(pages, by_url):
    posts = sorted([p for p in pages if p["type"] == "blog"],
                   key=lambda p: (p["published"], p["url"]), reverse=True)
    order = ["POS buying guides", "Loss prevention", "Operations", "Inventory & finance", "Africa", "En français"]
    cats = sorted({p["category"] for p in posts}, key=lambda c: order.index(c) if c in order else len(order))
    sections = []
    for c in cats:
        cards = "\n".join(card_html(p, p["lang"]) for p in posts if p["category"] == c)
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
        path = os.path.join(repo, p["output"]) if p.get("output") else os.path.join(repo, p["url"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(html_out)
        report.append((p["url"], p["lang"], p["type"], words, len(p["title"]), len(p["description"])))
    if any(p["type"] == "blog" for p in pages):
        path = os.path.join(repo, "blog", "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(blog_index(pages, by_url))
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

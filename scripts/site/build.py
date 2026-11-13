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
# Support line for installation and setup help (WhatsApp or phone)
SUPPORT_PHONE = "+237 679 690 703"
SUPPORT_LINK = ('<a href="https://wa.me/237679690703" target="_blank" rel="noopener">WhatsApp '
                + SUPPORT_PHONE + '</a> (<a href="tel:+237679690703">call</a>)')
# Hand-maintained pages that generated pages may reference as hreflang alternates
MANUAL_PAGES = {"/", "/solutions/", "/fr/solutions/"}
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
        "setup_help": "Need help installing or setting up LoungeOS for your business? Message or call us on",
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
        "setup_help": "Besoin d'aide pour installer ou configurer LoungeOS pour votre commerce ? Écrivez-nous ou appelez le",
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

LOGIN = "https://app.loungeos.app/login"

# Shopify-style mega menus. Each menu: (label, columns, featured card). A column
# is (heading, [(icon, title, one-line description, url)]). Icons are in _I.
MEGA = {
    "en": {
        "badge": "POS &amp; Business",
        "menus": [
            ("Product", [
                ("Sell", [
                    ("receipt", "Point of sale", "Fast till for touch and mouse", "/features/"),
                    ("wifi-off", "Offline selling", "Keeps selling without internet", "/features/offline-pos/"),
                    ("qr", "QR table ordering", "Guests order from their phone", "/features/qr-code-ordering/"),
                    ("wallet", "Mobile money &amp; payments", "Cash, MoMo, Orange Money, card", "/features/mobile-money-pos/"),
                    ("credit", "Customer tabs", "Sell now, get paid later", "/features/customer-tabs/"),
                ]),
                ("Run your business", [
                    ("package", "Inventory", "Stock, suppliers and alerts", "/features/inventory-management/"),
                    ("kitchen", "Kitchen &amp; bar screens", "Orders straight to the right station", "/features/kitchen-display-system/"),
                    ("table", "Tables &amp; floors", "Areas, tables, split and move bills", "/features/table-management/"),
                    ("book", "Expenses &amp; accounting", "Books that follow every sale", "/features/restaurant-accounting/"),
                    ("shield", "Loss prevention", "Manager PINs and activity log", "/features/loss-prevention/"),
                ]),
                ("Grow", [
                    ("branch", "Several branches", "Every shop side by side", "/features/multi-branch/"),
                    ("phone", "Phone app", "Sales and alerts in your pocket", "/features/mobile-app/"),
                    ("download", "Download", "Windows, Mac, Android and web", "/download/"),
                ]),
            ], ("All features", "Everything LoungeOS does, in one place, in English and French.", "/features/", "See all features", "loungeos-pos-order-screen")),
            ("Solutions", [
                ("Food &amp; drink", [
                    ("utensils", "Restaurants", "Tables, kitchen and food cost", "/restaurant-pos/"),
                    ("wine", "Bars, lounges &amp; nightclubs", "Bottles, VIP tables, late nights", "/lounge-pos/"),
                    ("coffee", "Cafés &amp; fast food", "Counter orders in seconds", "/cafe-pos/"),
                    ("bed", "Hotels &amp; guest houses", "Restaurant, bar and room service", "/hotel-pos/"),
                ]),
                ("Shops", [
                    ("shirt", "Clothes, shoes &amp; boutiques", "Barcodes, stock and credit", "/retail-pos/"),
                    ("cart", "Supermarkets &amp; groceries", "Fast checkout, several tills", "/supermarket-pos/"),
                    ("pill", "Pharmacies", "Every box counted", "/pharmacy-pos/"),
                    ("hammer", "Hardware stores", "Builder credit and deliveries", "/hardware-store-pos/"),
                    ("boxes", "Wholesale &amp; depots", "Cartons, credit and depots", "/wholesale-pos/"),
                ]),
                ("Countries", [
                    ("globe", "Cameroon", "FCFA, MTN and Orange Money", "/cameroon/"),
                    ("globe", "Nigeria", "Naira and local payments", "/nigeria/"),
                    ("globe", "Ghana", "Cedi and mobile money", "/ghana/"),
                    ("globe", "South Africa", "Rand and load-shedding", "/south-africa/"),
                    ("globe", "Africa", "Across the continent", "/africa/"),
                ]),
            ], ("Every kind of business", "Pick yours to see its screens and its own price.", "/solutions/", "See all businesses", "loungeos-till-supermarket")),
            ("Resources", [
                ("Learn", [
                    ("help", "Help centre", "Step-by-step guides with screenshots", "/help/"),
                    ("news", "Blog", "Guides on running a tighter business", "/blog/"),
                    ("message", "FAQ", "Quick answers before you start", "/faq/"),
                ]),
                ("Compare", [
                    ("scale", "LoungeOS vs Loyverse", "An honest side-by-side", "/blog/loungeos-vs-loyverse/"),
                    ("scale", "Loyverse alternatives", "What else to look at", "/blog/loyverse-alternatives/"),
                    ("scale", "Best POS in Cameroon", "The options compared", "/blog/best-pos-systems-cameroon/"),
                ]),
                ("Company", [
                    ("info", "About", "Made by Sigalix in Cameroon", "/about/"),
                    ("message", "Contact", "Email, phone and WhatsApp", "/contact/"),
                    ("globe", "Français", "LoungeOS en français", "/fr/"),
                ]),
            ], ("Talk to us on WhatsApp", "Questions before you start? We answer in English and French.", "https://wa.me/237679690703", "Chat on WhatsApp", "loungeos-help-pos-cart")),
        ],
        "links": [("Pricing", "/pricing/"), ("Download", "/download/")],
        "login": "Log in", "cta": "Start free trial", "back": "Back", "menu": "Menu",
    },
    "fr": {
        "badge": "Logiciel de caisse",
        "menus": [
            ("Produit", [
                ("Vendre", [
                    ("receipt", "Caisse", "Rapide au toucher et à la souris", "/fr/fonctionnalites/"),
                    ("wifi-off", "Vente hors ligne", "Continue sans internet", "/fr/aide/hors-ligne-et-synchronisation/"),
                    ("qr", "Commande par QR code", "Les clients commandent depuis leur téléphone", "/fr/fonctionnalites/commande-qr-code/"),
                    ("wallet", "Mobile money et paiements", "Espèces, MoMo, Orange Money, carte", "/fr/aide/paiements-et-recus/"),
                    ("credit", "Ventes à crédit", "Vendez maintenant, encaissez plus tard", "/fr/fonctionnalites/ventes-a-credit/"),
                ]),
                ("Gérer", [
                    ("package", "Stocks", "Stock, fournisseurs et alertes", "/fr/aide/stocks-et-fournisseurs/"),
                    ("kitchen", "Écrans cuisine et bar", "Chaque commande au bon poste", "/fr/aide/ecrans-cuisine-et-bar/"),
                    ("table", "Tables et salles", "Zones, tables, additions partagées", "/fr/aide/tables-et-salles/"),
                    ("book", "Dépenses et comptabilité", "Des comptes qui suivent chaque vente", "/fr/aide/comptabilite/"),
                    ("shield", "Contrôle et sécurité", "PIN du responsable et journal", "/fr/aide/annuler-rembourser-approbation/"),
                ]),
                ("Grandir", [
                    ("branch", "Plusieurs établissements", "Chaque magasin côte à côte", "/fr/fonctionnalites/multi-etablissements/"),
                    ("phone", "Application mobile", "Ventes et alertes dans la poche", "/fr/fonctionnalites/application-mobile/"),
                    ("download", "Télécharger", "Windows, Mac, Android et web", "/fr/telecharger/"),
                ]),
            ], ("Toutes les fonctionnalités", "Tout ce que fait LoungeOS, en français et en anglais.", "/fr/fonctionnalites/", "Voir les fonctionnalités", "loungeos-help-fr-pos")),
            ("Solutions", [
                ("Restauration", [
                    ("utensils", "Restaurants", "Tables, cuisine et coût matière", "/fr/logiciel-caisse-restaurant/"),
                    ("wine", "Bars, lounges &amp; boîtes de nuit", "Bouteilles, tables VIP, nuits longues", "/fr/logiciel-gestion-bar-lounge/"),
                    ("coffee", "Cafés &amp; fast-food", "Commandes au comptoir en secondes", "/fr/logiciel-caisse-fast-food/"),
                    ("bed", "Hôtels &amp; auberges", "Restaurant, bar et room service", "/fr/logiciel-gestion-hotel/"),
                ]),
                ("Commerces", [
                    ("shirt", "Vêtements, chaussures &amp; boutiques", "Codes-barres, stock et crédit", "/fr/logiciel-caisse-boutique/"),
                    ("cart", "Supermarchés &amp; épiceries", "Caisse rapide, plusieurs caisses", "/fr/logiciel-caisse-supermarche/"),
                    ("pill", "Pharmacies", "Chaque boîte comptée", "/fr/logiciel-gestion-pharmacie/"),
                    ("hammer", "Quincailleries", "Crédit et livraisons", "/fr/logiciel-caisse-quincaillerie/"),
                    ("boxes", "Commerce de gros &amp; dépôts", "Cartons, crédit et dépôts", "/fr/logiciel-gestion-commerce-de-gros/"),
                ]),
                ("Pays", [
                    ("globe", "Cameroun", "FCFA, MTN et Orange Money", "/fr/cameroun/"),
                    ("globe", "Côte d'Ivoire", "FCFA et mobile money", "/fr/cote-divoire/"),
                    ("globe", "Sénégal", "FCFA, Wave et Orange Money", "/fr/senegal/"),
                    ("globe", "Afrique francophone", "Partout sur le continent", "/fr/afrique/"),
                ]),
            ], ("Chaque type d'activité", "Choisissez la vôtre pour voir ses écrans et son prix.", "/fr/solutions/", "Voir toutes les activités", "loungeos-till-supermarket")),
            ("Ressources", [
                ("Apprendre", [
                    ("help", "Centre d'aide", "Guides pas à pas avec captures", "/fr/aide/"),
                    ("news", "Blog", "Conseils pour mieux gérer", "/blog/"),
                    ("message", "FAQ", "Réponses rapides avant de commencer", "/fr/faq/"),
                ]),
                ("Comparer", [
                    ("scale", "LoungeOS ou Loyverse", "Comparaison honnête", "/fr/blog/loungeos-ou-loyverse/"),
                    ("scale", "Meilleur logiciel au Cameroun", "Les options comparées", "/fr/blog/meilleur-logiciel-caisse-cameroun/"),
                    ("scale", "Gestion de stock au Cameroun", "Le guide", "/fr/blog/logiciel-gestion-stock-cameroun/"),
                ]),
                ("Entreprise", [
                    ("info", "À propos", "Conçu par Sigalix au Cameroun", "/about/"),
                    ("message", "Contact", "E-mail, téléphone et WhatsApp", "/contact/"),
                    ("globe", "English", "LoungeOS in English", "/"),
                ]),
            ], ("Écrivez-nous sur WhatsApp", "Une question avant de commencer ? Nous répondons en français et en anglais.", "https://wa.me/237679690703", "Discuter sur WhatsApp", "loungeos-help-fr-pos-cart")),
        ],
        "links": [("Tarifs", "/fr/tarifs/"), ("Télécharger", "/fr/telecharger/")],
        "login": "Connexion", "cta": "Essai gratuit", "back": "Retour", "menu": "Menu",
    },
}


def nav_urls():
    """Every internal URL in the menus (build.py checks they exist)."""
    out = set()
    for m in MEGA.values():
        for _, cols, feat in m["menus"]:
            out.add(feat[2])
            for _, items in cols:
                out.update(i[3] for i in items)
        out.update(u for _, u in m["links"])
    return {u for u in out if u.startswith("/")}


def mega_menu(i, label, cols, feat, lang):
    back = MEGA[lang]["back"]
    cols_html = []
    for heading, items in cols:
        lis = "\n".join(
            f'<li><a class="mega-item" href="{u}">{icon(ic, "mega-icon")}<span><strong>{t}</strong>'
            f'<small>{d}</small></span></a></li>' for ic, t, d, u in items)
        cols_html.append(f'<div class="mega-col"><p class="mega-heading">{heading}</p><ul>\n{lis}\n</ul></div>')
    ext = ' target="_blank" rel="noopener"' if feat[2].startswith("http") else ""
    pic = (f'<img src="/images/screens/{feat[4]}-800.webp" alt="" width="800" height="430" loading="lazy" decoding="async" />'
           if len(feat) > 4 else "")
    feat_html = (f'<a class="mega-feature" href="{feat[2]}"{ext}>{pic}<strong>{feat[0]}</strong><span>{feat[1]}</span>'
                 f'<em>{feat[3]} {ARROW}</em></a>')
    return f"""          <div class="nav-dropdown mega" data-mega="{i}">
            <button type="button" class="nav-dropdown-toggle" aria-expanded="false" aria-controls="mega-{i}">{label} {CHEVRON}</button>
            <div class="mega-panel" id="mega-{i}">
              <div class="mega-inner">
                <button type="button" class="mega-back">‹ {back}</button>
                <p class="mega-title">{label}</p>
                <div class="mega-cols">
{chr(10).join(cols_html)}
                </div>
                <div class="mega-side">{feat_html}</div>
              </div>
            </div>
          </div>"""


def nav_html(lang):
    n = MEGA[lang]
    home = "/fr/" if lang == "fr" else "/"
    menus = "\n".join(mega_menu(i, label, cols, feat, lang) for i, (label, cols, feat) in enumerate(n["menus"]))
    links = "\n".join(f'          <a class="nav-plain" href="{u}">{t}</a>' for t, u in n["links"])
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
{menus}
{links}
          <div class="nav-mobile-cta">
            <a href="{SIGNUP}" class="btn btn-primary">{n['cta']}</a>
            <a href="{LOGIN}" class="btn btn-secondary">{n['login']}</a>
          </div>
        </div>

        <div class="nav-cta">
          <div class="lang-selector">
            {GLOBE}
            <select id="customLangSelect" aria-label="{sel_label}" onchange="changeLanguage(this.value)">
{opts}
            </select>
          </div>
          <a href="{LOGIN}" class="nav-login" id="navLoginBtn">{n['login']}</a>
          <a href="{SIGNUP}" class="btn btn-primary btn-sm" id="navCtaBtn">{n['cta']}</a>
        </div>

        <button class="menu-toggle" id="menuToggle" aria-expanded="false" aria-controls="navLinks" aria-label="{'Ouvrir le menu' if lang == 'fr' else 'Toggle navigation menu'}">
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
                           ("Clothing &amp; Shoe Store POS", "/retail-pos/"), ("Supermarket POS", "/supermarket-pos/"),
                           ("Pharmacy POS", "/pharmacy-pos/"), ("Hardware Store POS", "/hardware-store-pos/"),
                           ("Wholesale POS", "/wholesale-pos/"), ("All businesses", "/solutions/")]),
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
                           ("Caisse fast-food &amp; café", "/fr/logiciel-caisse-fast-food/"),
                           ("Logiciel de gestion hôtel", "/fr/logiciel-gestion-hotel/"),
                           ("Caisse boutique de vêtements", "/fr/logiciel-caisse-boutique/"),
                           ("Caisse supermarché", "/fr/logiciel-caisse-supermarche/"),
                           ("Logiciel pharmacie", "/fr/logiciel-gestion-pharmacie/"),
                           ("Caisse quincaillerie", "/fr/logiciel-caisse-quincaillerie/"),
                           ("Commerce de gros", "/fr/logiciel-gestion-commerce-de-gros/"),
                           ("Toutes les activités", "/fr/solutions/")]),
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


def offer(name, price, cur, months=None, url="/pricing/"):
    o = {"@type": "Offer", "name": name, "price": str(price), "priceCurrency": cur,
         "availability": "https://schema.org/InStock", "url": SITE + url}
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


# Live prices from the admin panel (account.loungeos.app/api/plans), copied into
# prices.json by sync_prices.py. Admin can give a plan its own price per business
# type; by default every type pays the plan's price. PRICES above is the fallback.
PRICES_FILE = os.path.join(HERE, "prices.json")
try:
    LIVE_PRICES = json.load(open(PRICES_FILE, encoding="utf-8")).get("tiers") or {}
except (OSError, ValueError):
    LIVE_PRICES = {}


def tier_prices(key, biz_type=None):
    """(US$/month, US$/year, FCFA/month, FCFA/year) of a plan for one business type."""
    row = next(r for r in PRICES if r[0] == key)
    live = LIVE_PRICES.get(key)
    if not live:
        return tuple(row[4:8])
    p = (live.get("types") or {}).get(biz_type) if biz_type else None
    p = p or live["plan"]
    return (p["USD"]["monthly"], p["USD"]["yearly"], p["XAF"]["monthly"], p["XAF"]["yearly"])


def from_prices(key):
    """The lowest prices of a plan across every business type ("From ...")."""
    options = [tier_prices(key)] + [tier_prices(key, t) for t in (LIVE_PRICES.get(key, {}).get("types") or {})]
    return min(options)


def plan_offers(biz_type=None, url="/pricing/", label=""):
    offers = [offer(f"{TRIAL_DAYS}-day free trial (Business features)", 0, "USD", url=url)]
    for key, name, *_ in PRICES:
        usd_m, usd_y, xaf_m, xaf_y = tier_prices(key, biz_type)
        name = f"{name}{label}"
        offers += [offer(f"{name} monthly", usd_m, "USD", 1, url),
                   offer(f"{name} yearly", usd_y, "USD", 12, url),
                   offer(f"{name} monthly (Cameroon)", xaf_m, "XAF", 1, url),
                   offer(f"{name} yearly (Cameroon)", xaf_y, "XAF", 12, url)]
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


def page_cta_title(page):
    """Shops and hotels get a call to action in their own words, not a restaurant's."""
    fam = next((f for k, f, *_ in BUSINESS_TYPES if k == page.get("biz_type")), None)
    fr = page["lang"] == "fr"
    if fam == "shop":
        return "Faites tourner votre commerce avec LoungeOS" if fr else "Run your shop on LoungeOS"
    if fam == "hotel":
        return "Faites tourner votre hôtel avec LoungeOS" if fr else "Run your hotel's outlets on LoungeOS"
    return None


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
    md = md.replace("[[cta]]", cta_box(lang, page_cta_title(page)))
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
    for key, name, *_ in PRICES:
        usd_m, usd_y, xaf_m, xaf_y = tier_prices(key)
        cells = [money(usd_m, "USD", lang), money(usd_y, "USD", lang),
                 money(xaf_m, "XAF", lang), money(xaf_y, "XAF", lang)]
        rows.append(f"<tr><td>{name}</td>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    table = f"<table>\n<thead>{head}</thead>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>"
    # Kinds of business that admin priced differently
    own = []
    for key, *_ in TYPE_PAGES:
        prices = [tier_prices(k, key) for k, *_ in PRICES]
        if prices != [tier_prices(k) for k, *_ in PRICES]:
            amounts = " / ".join(f"{money(p[0], 'USD', lang)} ({money(p[2], 'XAF', lang)})" for p in prices)
            sep = " :" if lang == "fr" else ":"
            own.append(f'<a href="{type_url(key, lang)}">{type_name(key, lang)}</a>{sep} {amounts}')
    if own:
        intro = ("Prix par mois de Starter / Business / Pro pour les activités qui ont leur propre tarif :" if lang == "fr"
                 else "Monthly Starter / Business / Pro prices for the kinds of business with their own price:")
        table += f"\n<p>{intro}</p>\n<ul>\n" + "\n".join(f"<li>{o}</li>" for o in own) + "\n</ul>"
    return table


PLAN_FEATURES = {
    "en": {
        "starter": ["Point of sale (POS)", "Inventory and suppliers",
                    "Customer tabs (pay later)", "Receipts", "Daily reports"],
        "business": ["Everything in Starter", "Expenses and accounting", "Weekly and monthly reports",
                     "QR code table ordering", "Shifts and cash control (coming soon)"],
        "pro": ["Everything in Business", "Several branches", "All-branches sales overview",
                "Priority support", "Payroll (coming soon)"],
    },
    "fr": {
        "starter": ["Caisse (point de vente)", "Stocks et fournisseurs",
                    "Comptes clients (payer plus tard)", "Reçus", "Rapports journaliers"],
        "business": ["Tout ce que propose Starter", "Dépenses et comptabilité", "Rapports hebdomadaires et mensuels",
                     "Commande par QR code à table", "Services et contrôle de caisse (bientôt disponible)"],
        "pro": ["Tout ce que propose Business", "Plusieurs succursales", "Vue des ventes de toutes les succursales",
                "Support prioritaire", "Paie (bientôt disponible)"],
    },
}

# The business-type switcher on the price cards. Keys are the app's business
# types (keep in sync with TYPE_FAMILY in /app.js). Each family words the first
# Starter line for that kind of business; only features the app has today.
BUSINESS_TYPES = [
    # key, family, English, French
    ("restaurant", "food", "Restaurant", "Restaurant"),
    ("lounge", "food", "Lounge or bar", "Lounge ou bar"),
    ("cafe", "food", "Café or fast food", "Café ou fast-food"),
    ("hotel", "hotel", "Hotel", "Hôtel"),
    ("retail", "shop", "Clothes and shoes", "Vêtements et chaussures"),
    ("supermarket", "shop", "Supermarket", "Supermarché"),
    ("pharmacy", "shop", "Pharmacy", "Pharmacie"),
    ("hardware", "shop", "Hardware", "Quincaillerie"),
    ("wholesale", "shop", "Wholesale", "Commerce de gros"),
    ("other", "shop", "Other", "Autre"),
]
FAMILY_LINE = {
    "en": {"all": "Point of sale (POS) for any kind of business",
           "food": "Point of sale (POS), tables, kitchen and bar screens",
           "hotel": "Point of sale for the restaurant and bar (rooms and bookings coming soon)",
           "shop": "Point of sale (POS) with barcode scanning"},
    "fr": {"all": "Caisse (point de vente) pour tout type d'activité",
           "food": "Caisse, tables, écrans cuisine et bar",
           "hotel": "Caisse du restaurant et du bar (chambres et réservations bientôt disponibles)",
           "shop": "Caisse avec lecture des codes-barres"},
}

# Plan lines that only apply to some families (space separated). The rest of
# the list applies to every kind of business.
FAMILY_ONLY = {
    "business": {"QR code table ordering": "food hotel",
                 "Commande par QR code à table": "food hotel"},
}


def plan_cards(lang, fixed=None):
    """Starter, Business and Pro cards with a business-type switcher and a
    monthly/yearly switch. The static HTML shows "From" US$ monthly prices;
    app.js switches to yearly on request, to FCFA for visitors in Cameroon and
    to the chosen business type's prices (admin can price a plan per type).
    app.js reads data-plan and writes .price, .price-from, .price-period and
    .price-savings, and the .billing-toggle and .type-switch state."""
    fr = lang == "fr"
    L = {
        "monthly": "Mensuel" if fr else "Monthly",
        "yearly": "Annuel" if fr else "Yearly",
        "free2": "2 mois offerts" if fr else "2 months free",
        "switch": "Payer à l'année (2 mois offerts)" if fr else "Pay yearly (2 months free)",
        "pm": "/ mois" if fr else "/ month",
        "from": "À partir de" if fr else "From",
        "popular": "Le plus choisi" if fr else "Most popular",
        "start": "Commencer l'essai gratuit" if fr else "Start free trial",
        "yousave": "Vous économisez" if fr else "You save",
        "yourtype": "Votre activité" if fr else "Your business",
        "all": "Toutes" if fr else "All",
        "note": (f"Chaque formule commence par un essai gratuit de {TRIAL_DAYS} jours avec les fonctionnalités "
                 "Business, sans paiement à l'avance. Les prix s'affichent en FCFA au Cameroun et en dollars US "
                 "partout ailleurs. Choisissez votre activité pour voir son prix exact."
                 if fr else
                 f"Every plan starts with a {TRIAL_DAYS}-day free trial with Business features. No payment up "
                 "front. Visitors in Cameroon see prices in FCFA, everyone else in US$. Pick your kind of "
                 "business to see its exact price."),
    }

    def li(items, families=None):
        out = []
        for i in items:
            fams = (families or {}).get(i)
            attr = f' class="family-item" data-families="{fams}"' if fams else ""
            out.append(f"<li{attr}>{CHECK} {i}</li>")
        return "\n".join(out)

    lines = FAMILY_LINE[lang]
    family_line = "".join(
        f'<span class="family-line" data-family="{fam}"{"" if fam == "all" else " hidden"}>{text}</span>'
        for fam, text in lines.items())

    if fixed:
        fam = next(f for k, f, *_ in BUSINESS_TYPES if k == fixed)
        family_line = "".join(
            f'<span class="family-line" data-family="{f_}"{"" if f_ == fam else " hidden"}>{text}</span>'
            for f_, text in lines.items())
    chips = [f'<button type="button" class="type-chip active" data-type="" aria-pressed="true">{L["all"]}</button>']
    for key, fam, en, fr_name in BUSINESS_TYPES:
        chips.append(f'<button type="button" class="type-chip" data-type="{key}" data-family="{fam}" '
                     f'aria-pressed="false">{fr_name if fr else en}</button>')
    chips = "\n  ".join(chips)

    cards = []
    for key, name, users, devices, *_ in PRICES:
        usd_m, usd_y, _, _ = tier_prices(key, fixed) if fixed else from_prices(key)
        featured = key == "business"
        badge = f'\n    <span class="price-card-badge">{L["popular"]}</span>' if featured else ""
        btn = "btn-accent" if featured else "btn-primary"
        save = money(usd_m * 12 - usd_y, "USD", lang)
        items = list(PLAN_FEATURES[lang][key])
        if key == "starter":
            items[0] = family_line
        features = [plan_seats(users, devices, lang)] + items
        # Lines only some kinds of business get (hidden when another type is picked)
        families = {i: fams for i, fams in FAMILY_ONLY.get(key, {}).items()}
        if fixed:  # lines this type doesn't get are left out
            items = [i for i in items if i not in families or fam in families[i].split()]
            features = [plan_seats(users, devices, lang)] + items
            families = {}
        cards.append(f"""  <div class="price-card{' featured' if featured else ''}" data-plan="{key}">{badge}
    <h3>{name}</h3>
    <div class="price-from"{' hidden' if fixed else ''}>{L['from']}</div>
    <div class="price">{money(usd_m, "USD", lang)}</div>
    <div class="price-period">{L['pm']}</div>
    <div class="price-savings" hidden>{L['yousave']} {save}</div>
    <ul class="price-features">{li(features, families)}</ul>
    <a href="{SIGNUP}" class="btn {btn}">{L['start']}</a>
  </div>""")
    cards = "\n".join(cards)
    switch = f"""<div class="type-switch" role="group" aria-label="{L['yourtype']}">
  <span class="type-switch-label">{L['yourtype']}</span>
  {chips}
</div>""" if not fixed else ""
    note = L["note"] if not fixed else L["note"].rsplit(". ", 1)[0] + "."
    return f"""<div class="plans-breakout"{f' data-fixed-type="{fixed}"' if fixed else ''}>
{switch}
<div class="billing-toggle">
  <span class="active" data-billing="monthly">{L['monthly']}</span>
  <button type="button" class="toggle-switch" role="switch" aria-checked="false" aria-label="{L['switch']}"></button>
  <span data-billing="yearly">{L['yearly']}</span>
  <span class="yearly-badge">{L['free2']}</span>
</div>
<div class="pricing-grid pricing-grid-3" style="margin: 0 auto 1.5rem;">
{cards}
</div>
</div><p class="region-price-note">{note}</p>"""

# ---------------------------------------------------------------- business-type landing pages
# One landing page per business type of the app (LoungeOS src/lib/business-types.ts,
# "other" excepted), in English and French. Each shows that type's own prices,
# which admin can set per type on account.loungeos.app. Keys = BUSINESS_TYPES above.
TYPE_PAGES = [
    # key, icon, English name, French name, English page, French page
    ("restaurant", "utensils", "Restaurants", "Restaurants", "/restaurant-pos/", "/fr/logiciel-caisse-restaurant/"),
    ("lounge", "wine", "Bars, lounges &amp; nightclubs", "Bars, lounges &amp; boîtes de nuit", "/lounge-pos/", "/fr/logiciel-gestion-bar-lounge/"),
    ("cafe", "coffee", "Cafés &amp; fast food", "Cafés &amp; fast-food", "/cafe-pos/", "/fr/logiciel-caisse-fast-food/"),
    ("hotel", "bed", "Hotels &amp; guest houses", "Hôtels &amp; auberges", "/hotel-pos/", "/fr/logiciel-gestion-hotel/"),
    ("retail", "shirt", "Clothes, shoes &amp; boutiques", "Vêtements, chaussures &amp; boutiques", "/retail-pos/", "/fr/logiciel-caisse-boutique/"),
    ("supermarket", "cart", "Supermarkets &amp; groceries", "Supermarchés &amp; épiceries", "/supermarket-pos/", "/fr/logiciel-caisse-supermarche/"),
    ("pharmacy", "pill", "Pharmacies", "Pharmacies", "/pharmacy-pos/", "/fr/logiciel-gestion-pharmacie/"),
    ("hardware", "hammer", "Hardware stores", "Quincailleries", "/hardware-store-pos/", "/fr/logiciel-caisse-quincaillerie/"),
    ("wholesale", "boxes", "Wholesale &amp; depots", "Commerce de gros &amp; dépôts", "/wholesale-pos/", "/fr/logiciel-gestion-commerce-de-gros/"),
]
SOLUTIONS_URL = {"en": "/solutions/", "fr": "/fr/solutions/"}


def type_page(key):
    return next(t for t in TYPE_PAGES if t[0] == key)


def type_name(key, lang):
    t = type_page(key)
    return t[3] if lang == "fr" else t[2]


def type_url(key, lang):
    t = type_page(key)
    return t[5] if lang == "fr" else t[4]


_I = {
    "utensils": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
    "wine": '<path d="M8 22h8"/><path d="M7 10h10"/><path d="M12 15v7"/><path d="M12 15a5 5 0 0 0 5-5c0-2-.5-4-2-8H9c-1.5 4-2 6-2 8a5 5 0 0 0 5 5Z"/>',
    "coffee": '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/>',
    "bed": '<path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/>',
    "shirt": '<path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "pill": '<path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/>',
    "hammer": '<path d="m15 12-8.5 8.5c-.83.83-2.17.83-3 0 0 0 0 0 0 0a2.12 2.12 0 0 1 0-3L12 9"/><path d="M17.64 15 22 10.64"/><path d="m20.91 11.7-1.25-1.25c-.6-.6-.93-1.4-.93-2.25v-.86L16.01 4.6a5.56 5.56 0 0 0-3.94-1.64H9l.92.82A6.18 6.18 0 0 1 12 8.4v1.56l2 2h2.47l2.26 1.91"/>',
    "boxes": '<path d="M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0L12 19v-5.5l-5-3-4.03 2.42Z"/><path d="m7 16.5-4.74-2.85"/><path d="m7 16.5 5-3"/><path d="M7 16.5v5.17"/><path d="M12 13.5V19l3.97 2.38a2 2 0 0 0 2.06 0l3-1.8a2 2 0 0 0 .97-1.71v-3.24a2 2 0 0 0-.97-1.71L17 10.5l-5 3Z"/><path d="m17 16.5-5-3"/><path d="m17 16.5 4.74-2.85"/><path d="M17 16.5v5.17"/><path d="M7.97 4.42A2 2 0 0 0 7 6.13v4.37l5 3 5-3V6.13a2 2 0 0 0-.97-1.71l-3-1.8a2 2 0 0 0-2.06 0l-3 1.8Z"/><path d="M12 8 7.26 5.15"/><path d="m12 8 4.74-2.85"/><path d="M12 13.5V8"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M8 7v10"/><path d="M12 7v10"/><path d="M16 7v10"/>',
    "wifi-off": '<path d="M12 20h.01"/><path d="M8.5 16.43a5 5 0 0 1 7 0"/><path d="M2 8.82a15 15 0 0 1 4.18-2.65"/><path d="M19 12.86a10 10 0 0 0-2.27-1.62"/><path d="M5 12.86a10 10 0 0 1 5.17-2.69"/><path d="M10.71 5.05A16 16 0 0 1 22 8.82"/><line x1="2" x2="22" y1="2" y2="22"/>',
    "phone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "receipt": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/>',
    "package": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "tag": '<path d="M12.59 2.59A2 2 0 0 0 11.17 2H4a2 2 0 0 0-2 2v7.17a2 2 0 0 0 .59 1.42l8.7 8.7a2.43 2.43 0 0 0 3.42 0l6.58-6.58a2.43 2.43 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "qr": '<rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/>',
    "store": '<path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/><path d="M2 7h20"/><path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "printer": '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"/><rect x="6" y="14" width="12" height="8" rx="1"/>',
    "kitchen": '<path d="M17 21a1 1 0 0 0 1-1v-5.35c0-.457.316-.844.727-1.041a4 4 0 0 0-2.134-7.589 5 5 0 0 0-9.186 0 4 4 0 0 0-2.134 7.588c.411.198.727.585.727 1.041V20a1 1 0 0 0 1 1Z"/><path d="M6 17h12"/>',
    "table": '<path d="M3 9h18"/><path d="M5 9v12"/><path d="M19 9v12"/><path d="M3 5h18v4H3z"/>',
    "credit": '<rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    "branch": '<path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "music": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "news": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
}


def icon(name, cls="ind-icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')


IND_T = {
    "en": {"for": "LoungeOS for", "problem": "Sound familiar?", "does": "What LoungeOS does for you",
           "soon": "Coming next", "soon_note": "Not in the app yet. We say so here, so you can decide with the facts.",
           "pricing": "Pricing for {name}", "pricing_sub": "The price of each plan for this kind of business, straight from our price list.",
           "compare": "Compare prices for every kind of business →", "others": "LoungeOS for other businesses",
           "all": "All kinds of business", "pick": "What kind of business do you run?"},
    "fr": {"for": "LoungeOS pour", "problem": "Ça vous parle ?", "does": "Ce que LoungeOS fait pour vous",
           "soon": "Bientôt disponible", "soon_note": "Pas encore dans l'application. Nous le disons ici pour que vous choisissiez en connaissance de cause.",
           "pricing": "Tarifs pour {name}", "pricing_sub": "Le prix de chaque formule pour ce type d'activité, tiré directement de notre grille tarifaire.",
           "compare": "Comparer les prix de chaque type d'activité →", "others": "LoungeOS pour d'autres activités",
           "all": "Tous les types d'activité", "pick": "Quel type d'activité gérez-vous ?"},
}


def md_inline(text):
    return markdown.markdown(str(text))[3:-4]


def type_tiles(lang, current=None, desc=True):
    """Icon tiles linking to every business-type landing page."""
    tiles = []
    for key, ic, *_ in TYPE_PAGES:
        if key == current:
            continue
        url = type_url(key, lang)
        p = BY_URL.get(url, {})
        sub = f'<span>{esc(p.get("card_desc", ""))}</span>' if desc and p.get("card_desc") else ""
        tiles.append(f'<a class="type-tile" href="{url}">{icon(ic, "type-tile-icon")}'
                     f'<strong>{type_name(key, lang)}</strong>{sub}</a>')
    return '<div class="type-tiles">\n' + "\n".join(tiles) + "\n</div>"


def types_include(lang):
    return type_tiles(lang)


BY_URL = {}


def industry_sections(page):
    """The landing-page blocks above the long-form text: problems, features,
    what is still coming, and this type's prices."""
    lang = page["lang"]
    t = IND_T[lang]
    key = page["biz_type"]
    name = page.get("type_name") or type_name(key, lang)
    out = []
    if page.get("pains"):
        cards = "\n".join(
            f'<div class="pain-card"><h3>{esc(p[0])}</h3><p>{md_inline(p[1])}</p></div>' for p in page["pains"])
        out.append(f"""      <section class="ind-band ind-pains">
        <div class="container">
          <p class="section-label">{t['problem']}</p>
          <h2 class="section-title">{esc(page.get('pains_title', ''))}</h2>
          <div class="pain-grid">
{cards}
          </div>
        </div>
      </section>""")
    if page.get("features"):
        cards = "\n".join(
            f'<div class="feat-card">{icon(f[0])}<h3>{esc(f[1])}</h3><p>{md_inline(f[2])}</p></div>'
            for f in page["features"])
        soon = ""
        if page.get("soon"):
            lis = "\n".join(f"<li>{md_inline(s)}</li>" for s in page["soon"])
            soon = f"""<div class="soon-box">
            <h3>{icon('clock', 'ind-icon-sm')} {t['soon']}</h3>
            <ul>
{lis}
            </ul>
            <p>{t['soon_note']}</p>
          </div>"""
        out.append(f"""      <section class="ind-band">
        <div class="container">
          <p class="section-label">{t['does']}</p>
          <h2 class="section-title">{esc(page.get('features_title', ''))}</h2>
          <div class="feat-grid">
{cards}
          </div>
          {soon}
        </div>
      </section>""")
    compare = SOLUTIONS_URL[lang].replace("/solutions/", "/tarifs/" if lang == "fr" else "/pricing/")
    out.append(f"""      <section class="ind-band ind-pricing" id="pricing">
        <div class="container">
          <h2 class="section-title">{t['pricing'].format(name=page.get('pricing_name') or name.lower())}</h2>
          <p class="section-subtitle">{t['pricing_sub']}</p>
          {plan_cards(lang, fixed=key)}
          <p class="ind-compare"><a href="{compare}">{t['compare']}</a></p>
        </div>
      </section>""")
    return out


def industry_graph(page):
    """Structured data for a business-type page: LoungeOS for this kind of
    business, with this type's offers."""
    lang, url, key = page["lang"], page["url"], page["biz_type"]
    name = html.unescape(page.get("type_name") or type_name(key, lang))
    label = f" ({name})"
    app = {
        "@type": "SoftwareApplication", "@id": SITE + url + "#app",
        "name": html.unescape(page.get("app_name") or f"LoungeOS {'pour' if lang == 'fr' else 'for'} {name}"),
        "url": SITE + url, "applicationCategory": "BusinessApplication",
        "applicationSubCategory": html.unescape(page.get("label", "")),
        "operatingSystem": SOFTWARE["operatingSystem"], "softwareVersion": APP_VERSION,
        "inLanguage": ["en", "fr"], "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": SOFTWARE_ID},
        "audience": {"@type": "BusinessAudience", "audienceType": name},
        "description": page["description"],
        "offers": plan_offers(key, url, label),
    }
    if page.get("features"):
        app["featureList"] = [f[1] for f in page["features"]]
    if page.get("image"):
        app["screenshot"] = f"{SITE}/images/screens/{page['image']}.webp"
    return app


def solutions_index(lang):
    fr = lang == "fr"
    url = SOLUTIONS_URL[lang]
    t = T[lang]
    page = {
        "url": url, "lang": lang, "type": "solutions-index",
        "alternates": {"en": SOLUTIONS_URL["en"], "fr": SOLUTIONS_URL["fr"]},
        "title": ("Logiciel de caisse pour chaque type de commerce | LoungeOS" if fr else
                  "POS for Every Kind of Business: Food, Shops, Hotels | LoungeOS"),
        "description": ("Restaurant, bar, hôtel, boutique de vêtements, supermarché, pharmacie, quincaillerie ou commerce de gros : choisissez votre activité et voyez ses écrans et ses prix."
                        if fr else
                        "Restaurant, bar, hotel, clothes shop, supermarket, pharmacy, hardware store or wholesale: pick your kind of business and see its screens and its prices."),
        "h1": "Une caisse taillée pour votre activité" if fr else "A point of sale made for your kind of business",
        "lead": ("Le même LoungeOS, avec les bons écrans et les bons mots pour chaque commerce. Choisissez le vôtre pour voir ce qu'il fait pour vous et combien il coûte."
                 if fr else
                 "The same LoungeOS, with the right screens and the right words for each kind of business. Pick yours to see what it does for you and what it costs."),
        "label": "Solutions", "modified": TODAY.isoformat(), "no_hero_cta": True,
    }
    crumbs = [(t["home"], "/fr/" if fr else "/"), ("Solutions", url)]
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + type_url(k, lang),
              "name": html.unescape(type_name(k, lang))} for i, (k, *_) in enumerate(TYPE_PAGES)]
    graph = [ORG, WEBSITE,
             {"@type": ["WebPage", "CollectionPage"], "@id": SITE + url + "#webpage", "url": SITE + url,
              "name": page["title"], "description": page["description"], "inLanguage": lang,
              "isPartOf": {"@id": WEBSITE_ID}, "breadcrumb": {"@id": SITE + url + "#breadcrumb"},
              "dateModified": page["modified"], "about": {"@id": SOFTWARE_ID},
              "mainEntity": {"@type": "ItemList", "itemListElement": items}},
             SOFTWARE, breadcrumb_node(url, crumbs)]
    how = [("store", "Un seul compte, plusieurs activités" if fr else "One account, any mix of businesses",
            "Un hôtel avec un restaurant, une boutique avec un bar : cochez tout ce que vous faites dans l'assistant de configuration."
            if fr else "A hotel with a restaurant, a shop with a bar: tick everything you do in the setup wizard."),
           ("layers", "Les bons écrans" if fr else "The right screens",
            "Tables, cuisine et bar pour la restauration ; produits et codes-barres pour les commerces. Le reste se masque."
            if fr else "Tables, kitchen and bar for food; products and barcodes for shops. What you don't need stays out of the way."),
           ("tag", "Un prix par activité" if fr else "A price for each kind of business",
            "Chaque page affiche le prix de votre activité. Aujourd'hui, toutes les activités paient le même prix."
            if fr else "Each page shows your kind of business's own price. Today every kind of business pays the same.")]
    how_html = "\n".join(f'<div class="feat-card">{icon(i)}<h3>{a}</h3><p>{b}</p></div>' for i, a, b in how)
    other = ("Votre activité n'est pas dans la liste ? Choisissez « Autre activité » à l'inscription : vous avez la caisse, les stocks, l'équipe et les rapports, et vous activez les écrans dont vous avez besoin."
             if fr else
             "Not on the list? Pick “Something else” when you sign up: you get the till, stock, team and reports, and switch on the screens you need.")
    out = [head_html(page, graph), "  <body>", nav_html(lang), '    <main id="main-content">',
           hero_html(page, crumbs),
           f'      <section class="ind-band" style="padding-top: 0"><div class="container">{type_tiles(lang)}'
           f'<p class="ind-compare">{other}</p></div></section>',
           f'      <section class="ind-band ind-pains"><div class="container"><h2 class="section-title">'
           f'{"Un logiciel, chaque commerce" if fr else "One app, every kind of business"}</h2>'
           f'<div class="feat-grid">{how_html}</div></div></section>',
           f'      <section class="ind-band ind-pricing" id="pricing"><div class="container"><h2 class="section-title">'
           f'{"Tarifs" if fr else "Pricing"}</h2>{plan_cards(lang)}</div></section>',
           f'      <section style="padding: 0 1.5rem 1rem">{cta_box(lang)}</section>',
           "    </main>", footer_html(lang), tail_scripts(lang), "  </body>", "</html>", ""]
    html_out = "\n".join(out)
    return url, (fr_typography(html_out) if fr else html_out)


INCLUDES = {"price_table": price_table, "plans": plan_cards, "types": types_include}


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
        <p class="trust-line">{t['trust']}</p>
        <p class="help-line">{t['setup_help']} {SUPPORT_LINK}</p>""" if not page.get("no_hero_cta") else ""
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
    if page["type"] in ("feature", "solution", "region", "core", "home-fr", "industry"):
        pnode["about"] = {"@id": SOFTWARE_ID}
        graph.append(SOFTWARE)
    if page["type"] == "industry":
        pnode["about"] = {"@id": SITE + url + "#app"}
        graph.append(industry_graph(page))
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
        if page["type"] == "industry":
            parts += industry_sections(page)
        parts.append(f"""      <section class="content-section">
        <div class="prose prose-wide">
{body}
        </div>
      </section>""")
        if not page.get("no_cta"):
            parts.append(f'      <section style="padding: 0 1.5rem 1rem">{cta_box(lang, page_cta_title(page))}</section>')

    if page["type"] == "industry":
        parts.append(f"""      <section class="ind-band ind-others">
        <div class="container">
          <h2 class="section-title">{IND_T[lang]['others']}</h2>
          {type_tiles(lang, current=page['biz_type'], desc=False)}
          <p class="ind-compare"><a href="{SOLUTIONS_URL[lang]}">{IND_T[lang]['all']} →</a></p>
        </div>
      </section>""")
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
    BY_URL.update(by_url)
    for key, *_ in TYPE_PAGES:
        for lang in ("en", "fr"):
            u = type_url(key, lang)
            if u not in by_url and not LENIENT:
                raise SystemExit(f"business type {key}: page {u} not found")
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
    for u in sorted(nav_urls()):
        if u not in by_url and u not in MANUAL_PAGES and not os.path.exists(os.path.join(repo, u.strip("/"), "index.html")):
            raise SystemExit(f"menu link {u} not found")
    # Hand-edited pages get the same menu as the generated ones
    for name in ("index.html", "accessibility.html", "legal.html", "privacy.html", "terms.html"):
        path = os.path.join(repo, name)
        h = open(path, encoding="utf-8").read()
        h2 = re.sub(r'    <a class="skip-link".*?</nav>', lambda m: nav_html("en"), h, count=1, flags=re.S)
        if h2 != h:
            open(path, "w", encoding="utf-8").write(h2)
    # The homepage (hand-edited) shows the same business-type tiles
    home = os.path.join(repo, "index.html")
    h = open(home, encoding="utf-8").read()
    h2 = re.sub(r"(<!-- type-tiles:start -->).*?(\s*<!-- type-tiles:end -->)",
                lambda m: m.group(1) + "\n" + type_tiles("en") + m.group(2), h, flags=re.S)
    if h2 != h:
        open(home, "w", encoding="utf-8").write(h2)
    for lang in ("en", "fr"):
        url, out = solutions_index(lang)
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

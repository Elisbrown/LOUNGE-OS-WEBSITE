# LoungeOS: product context

Site: https://loungeos.app
Product: point of sale and business management for restaurants, bars, lounges, cafés, hotels' food and drink outlets, shops and mini-markets, made by Sigalix (sigalix.com) in Cameroon.
Buyer: owner or manager of a small to mid-sized venue or shop, mainly in Cameroon and French- and English-speaking Africa, who loses money to theft, stock leaks and internet or power cuts.
Conversion: trial sign-up at https://app.loungeos.app/login (sign-up is on the sign-in page). Secondary: app download, demo request by email/phone.
Ship mode: PR for review (owner merges; main deploys to loungeos.app on Hostinger).

## Facts (source in brackets)

- Plans: Starter US$10/mo (6,000 FCFA), 2 users, 2 devices; Business US$25/mo (15,000 FCFA), 5 users, 5 devices; Pro US$50/mo (30,000 FCFA), unlimited users, 10+ devices. Yearly = 10x monthly. [scripts/site/build.py PRICES; app.js PLANS]
- 14-day free trial on every plan with Business features, no payment up front. [build.py TRIAL_DAYS]
- Business adds expenses and accounting (gated in app), weekly and monthly reports (reports over one day are gated, "reports_advanced"). [LoungeOS src/lib/plan-shared.ts]
- NOT BUILT as of 2026-11-11, so the site says "coming soon": shifts and cash control, email alerts, several branches, payroll. [LoungeOS claude/foundation; grep shows no shift module]
- Platforms: web app (app.loungeos.app), Windows 10/11 64-bit, Mac (Apple Silicon and Intel), Android 6+. Windows and Mac sell offline, read-only after 7 days without sync. [content/en/core/download.md, faq.md]
- Languages: app in English and French. [LoungeOS src/locales/en.json, fr.json]
- Business types in setup: lounge, restaurant, café, shop/boutique, supermarket/grocery, pharmacy, hardware, wholesale, hotel, other. Shops see "Products" instead of "Menu"; tables/kitchen/bar/events switch on per type. [LoungeOS src/lib/business-types.ts]
- Shipped in 2.0.7 to 2.0.9 (Nov 2026): barcode scanning, split bills (item, equal shares, amounts), move orders, guests per order, Pay later customer tabs, cash drawer open, kitchen/bar tickets printing only changes, manager approval or PIN for cancels/refunds/reopen/price changes, daily sales report, photo search (free images), English/French documents. [project notes loungeos-documents-2-0-8, loungeos-till-2-0-7]
- Not supported: weighed items, expiry dates and batches, hotel rooms/bookings/charge to room. [LoungeOS business-types.ts; project notes loungeos-feature-gaps]
- Payment methods are the business's own (cash, MTN MoMo, Orange Money, card...). LoungeOS records them; it does not process POS payments. [project notes]
- Contacts: info@sigalix.com, +237 689 699 688 (sales); support@loungeos.app, +237 679 690 703 (support); billing@sigalix.com. [content/en/core/contact.md]

## Competitors (first pass, 2026-11-11, from web search)

Who shows up for the queries LoungeOS should own:
- Directories: Capterra (.co.za, .fr), GetApp, SourceForge "restaurant POS Africa", appvizer.fr, tool-advisor.fr. LoungeOS is not listed on any of them.
- Products: Loyverse (free POS, big in Africa), Odoo POS (partners in Cameroon, MoMo modules), Lightspeed (FR-language pages), iKhokha (South Africa), kolonell.com (blog posts on POS in Douala and Accra, Nov 2026).
- To confirm with Search Console data once connected.

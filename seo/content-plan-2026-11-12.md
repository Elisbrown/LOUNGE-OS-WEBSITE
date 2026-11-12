# Website and SEO content plan (2026-11-12)

Asked by the owner on 2026-11-12: put every new feature on the public site, write new blogs, comparison and "best" articles with keyword targets, use real images, and rebuild the knowledge base and documentation so every step is accurate, with screenshots.

## What was wrong

- The knowledge base (`/knowledgebase.html`) and documentation (`/documentation.html`) were the same 1,800-line page twice, written for 2.0. Menu names, the till sign-in, the Android app and plan features had all changed since.
- The site said "several branches" was coming soon. Branches shipped in 2.1.3.
- Nothing on the site covered QR table ordering (2.1.1), the owner's mobile number at set-up (2.1.2), branches (2.1.3) or the new Android phone app with notifications and a widget (2.1.4).
- The download page still described the old Android app (needed Chrome) and said "2.0".
- Search intent with no page: "loungeos vs loyverse", "odoo pos alternative", "qr code ordering restaurant", "logiciel de gestion de stock cameroun", "cahier de crédit", "best pos system cameroon", multi-location management.

## What this round ships

1. **Help centre** generated from Markdown (`scripts/site/content/{en,fr}/help/`): `/help/` and `/fr/aide/`, 22 articles in each language, one task per article, numbered steps that match the 2.1.4 screens, screenshots from a fresh sample business (Viona Lounge, sample data). `/knowledgebase.html` and `/documentation.html` now point to it (301 in `.htaccess`, plus a canonical and a redirect page for hosts that ignore `.htaccess`).
2. **New feature pages (EN + FR)**: QR code table ordering, branches (multi-location), the phone app, customer tabs (pay later).
3. **Facts updated everywhere**: branches available on Pro, QR ordering on Business and Pro, phone app, owner mobile number, version 2.1.4, plan feature lists, download page and FAQ.
4. **New articles** (keyword in brackets):
   - LoungeOS vs Loyverse (loyverse vs loungeos, loyverse alternative), EN + FR
   - Best POS systems in Cameroon 2026 (best pos system cameroon / meilleur logiciel de caisse cameroun), EN + FR
   - Odoo POS alternatives for restaurants and bars (odoo pos alternative)
   - QR code ordering for restaurants: how it works (qr code ordering restaurant / commande qr code restaurant), EN + FR
   - How to manage several restaurant branches (manage multiple restaurant locations / gérer plusieurs restaurants), EN + FR
   - Customer tabs and credit sales (bar tab, cahier de crédit boutique), EN + FR
   - Run your business from your phone: notifications and widget (restaurant pos app android), EN + FR
   - Logiciel de gestion de stock au Cameroun (FR only, local query)
5. **Images**: all new screenshots are real captures of LoungeOS 2.1.4 (desktop at 1440×900, phone at 390×844), not mock-ups. Food photos in the sample menu are illustrations, as before.

## Rules kept

- Sample figures and staff names are labelled as sample data. Viona Lounge is a real customer: no real numbers are claimed.
- Not built, so still "coming soon": shifts and cash control, email alerts, payroll. Weighed items, expiry dates and hotel rooms are not claimed.
- Competitor facts link to the competitor's own pages and carry the date they were checked. Prices change: articles say to confirm on the vendor's site.
- No testimonials or ratings without real customers' permission.

## Next round

- Food cost / pour cost calculator (free tool).
- "Best bar POS systems" once each listed product's offline and Africa availability is checked.
- French versions of the remaining English feature pages (offline, inventory, KDS, accounting, loss prevention, mobile money).
- Retake help screenshots whenever the screens they show change (the release notes say which).

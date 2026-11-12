#!/usr/bin/env python3
"""Copy the live plan prices from the admin panel into scripts/site/prices.json.

The account site (account.loungeos.app/api/plans) holds each plan's price and,
when admin sets one, its own price per business type. Visitors' browsers read
those live (app.js); this file gives the same prices to the static HTML and the
JSON-LD offers that search engines read. The SEO refresh GitHub Action runs it
daily and rebuilds the pages when a price changed.

    python3 scripts/site/sync_prices.py      # exit 0: unchanged, 10: changed, 1: unreachable

When the account site can't be reached, prices.json is left as it is.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "prices.json")
URL = os.environ.get("PLANS_URL", "https://account.loungeos.app/api/plans")
TIERS = ("starter", "business", "pro")
# The app's business types (LoungeOS src/lib/business-types.ts)
TYPES = ("lounge", "restaurant", "cafe", "retail", "supermarket", "pharmacy", "hardware", "wholesale", "hotel", "other")


def static_prices():
    """The fallback prices in build.py, as {tier: {USD: {monthly, yearly}, XAF: {...}}}."""
    sys.path.insert(0, HERE)
    from build import PRICES  # noqa: E402
    return {k: {"USD": {"monthly": um, "yearly": uy}, "XAF": {"monthly": xm, "yearly": xy}}
            for k, _, _, _, um, uy, xm, xy in PRICES}


def resolve(plans, static):
    """Same rules as loadLivePrices() in /app.js: a type left out pays the plan's
    price; a missing US$ price is scaled from the FCFA one."""
    live = {}
    for pl in plans:
        tier = pl.get("code")
        if tier not in TIERS or pl.get("isTrial") or not (pl.get("basePrice") or 0) > 0:
            continue
        period = "yearly" if (pl.get("durationDays") or 0) >= 300 else "monthly"
        ref_xaf = static[tier]["XAF"][period]
        ref_usd = static[tier]["USD"][period]

        def usd_of(xaf, usd):
            if usd is not None and usd >= 0:
                return usd
            return round(ref_usd * xaf / ref_xaf)

        t = live.setdefault(tier, {"plan": {"USD": {}, "XAF": {}}, "types": {}})
        base = pl["basePrice"]
        t["plan"]["XAF"][period] = round(base)
        t["plan"]["USD"][period] = usd_of(base, pl.get("priceUsd"))
        try:
            own = json.loads(pl.get("typePrices") or "{}") or {}
        except ValueError:
            own = {}
        for typ, o in own.items():
            if typ not in TYPES or not isinstance(o, dict):
                continue
            x = o.get("basePrice") if o.get("basePrice") is not None else base
            if o.get("priceUsd") is not None:
                u = o["priceUsd"]
            elif o.get("basePrice") is not None:
                u = usd_of(x, None)
            else:
                u = t["plan"]["USD"][period]
            tt = t["types"].setdefault(typ, {"USD": {}, "XAF": {}})
            tt["XAF"][period] = round(x)
            tt["USD"][period] = u
    for tier, t in live.items():
        for period in ("monthly", "yearly"):
            for cur in ("USD", "XAF"):
                t["plan"][cur].setdefault(period, static[tier][cur][period])
                for typ in t["types"].values():
                    typ[cur].setdefault(period, t["plan"][cur][period])
    # Whole numbers stay whole in the JSON (no 6000.0)
    def clean(v):
        if isinstance(v, dict):
            return {k: clean(x) for k, x in sorted(v.items())}
        return int(v) if isinstance(v, float) and v.is_integer() else v
    return clean(live)


def main():
    static = static_prices()
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "loungeos-site-build", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            plans = json.load(r)
    except Exception as e:  # noqa: BLE001
        print(f"Could not read {URL}: {e}. prices.json left as it is.")
        return 1
    if not isinstance(plans, list):
        print("Unexpected answer from the account site. prices.json left as it is.")
        return 1
    tiers = resolve(plans, static)
    if not tiers:
        print("No paid plans found. prices.json left as it is.")
        return 1
    old = {}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
    if old.get("tiers") == tiers:
        print("Prices unchanged.")
        return 0
    data = {"source": URL, "fetched": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tiers": tiers}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("Prices changed: prices.json updated.")
    return 10


if __name__ == "__main__":
    sys.exit(main())

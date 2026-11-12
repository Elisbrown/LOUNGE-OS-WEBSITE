---
url: /help/offline-and-sync/
type: help
section: "Account, data and troubleshooting"
order: 1
title: "Selling Offline and Sync in LoungeOS (Power and Internet Cuts)"
description: "How the LoungeOS Windows and Mac tills keep selling without internet, sync when it returns, what the sync status means, and the 7-day offline limit."
h1: "Selling offline and sync"
lead: "The Windows and Mac tills keep everything on the computer and sell through internet cuts. When the connection comes back, they sync on their own."
card_title: "Selling offline and sync"
card_desc: "What works offline, the sync status, Sync now, the 7-day limit."
image: loungeos-help-pos-cart
published: 2026-11-12
modified: 2026-11-12
alternates:
  fr: /fr/aide/hors-ligne-et-synchronisation/
related:
  - /help/backups-and-your-data/
  - /blog/run-a-restaurant-during-power-and-internet-outages/
  - /features/offline-pos/
---

## Two copies of your data

Every business has two copies: one on each Windows or Mac till, and one online. They sync every few seconds when there is internet. The web app and the phone app work on the online copy.

## What works without internet

On the **Windows and Mac apps**, everything you need during service:

- taking orders, sending them to the kitchen and bar screens, printing tickets and receipts,
- payments in every method, Pay later tabs, refunds and approvals with a manager's PIN,
- stock coming off at each sale, receiving deliveries, expenses,
- the dashboard and reports for what this till recorded.

Phones, tablets and kitchen screens can keep working too, by opening the till in their browser over your Wi-Fi (`http://<till address>:2304`, see the [download page](/download/#connect-other-devices)).

What needs internet: the web app and the phone app, guest orders from the QR code, phone notifications, and seeing other tills' sales.

## The sync status

The cloud icon at the top of the till tells you where you stand:

- **Up to date**: everything is sent.
- **Syncing…**
- **Offline: changes are kept on this till**, with how many changes are waiting.
- **Not connected yet** or **Connect this till**: the till is not linked to your business online (see [Install LoungeOS](/help/install-loungeos/)).
- **Sync problem**: open it for details.

Press **Sync now** to send right away after the connection comes back. You never need to press it during normal service.

## The 7-day limit

A till that has not synced for 7 days becomes read-only: you can look at everything, but you can't record new sales until it reconnects. Connecting once, even through a phone hotspot for a minute, is enough to reset it. Nothing is ever deleted.

The same read-only mode applies when a subscription ends, until it is renewed.

## Power cuts

A laptop as the till rides through short power cuts on its battery. With a desktop computer, put the computer, the router and the receipt printer on a small UPS. Everything recorded before the power went is saved on the till.

## Frequently asked questions

### Two tills sold the same bottle while offline. What happens?

Both sales are kept, and stock goes down by both. Sales are never lost or overwritten by sync.

### Can I take orders on a tablet when the internet is down?

Yes, if the tablet opens the till in its browser over your Wi-Fi (`http://<till address>:2304`). The web app and the phone app need the internet.

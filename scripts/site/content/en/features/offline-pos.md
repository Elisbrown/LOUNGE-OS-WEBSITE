---
url: /features/offline-pos/
type: feature
title: "Offline POS System: Keep Selling Without Internet | LoungeOS"
description: "The LoungeOS Windows and Mac apps keep selling without internet. Orders, kitchen screens, payments and receipts keep working on your Wi-Fi and sync when you're back online."
h1: "An offline POS that keeps selling when the internet doesn't"
label: "Offline POS"
lead: "Most POS systems treat offline as an emergency mode with tight limits. The LoungeOS Windows and Mac apps keep your business's data on the computer, so the till keeps selling for up to 7 days without internet and syncs when the connection comes back."
image: loungeos-pos-menu-grid
image_alt: "LoungeOS point of sale menu grid that keeps selling without internet"
card_title: "Offline POS"
card_desc: "Windows and Mac tills keep selling without internet, with phones on your Wi-Fi, and sync when the connection comes back."
breadcrumb:
  - ["Features", "/features/"]
crumb: "Offline POS"
related:
  - /blog/cloud-vs-offline-pos/
  - /blog/best-offline-restaurant-pos-systems/
  - /blog/run-a-restaurant-during-power-and-internet-outages/
---

An **offline POS** is a point of sale system that keeps taking orders and payments when the internet connection is lost. The LoungeOS **Windows and Mac apps** do this by keeping your business's data on the computer as well as in the cloud. Phones, tablets and kitchen screens can talk to that computer over your own Wi-Fi, so an internet outage does not stop an order.

## How LoungeOS works without internet

1. **The till computer.** Install the LoungeOS app on a Windows 10 or 11 (64-bit) computer or a Mac, and sign in with your LoungeOS account. The app keeps your menu, tables, orders, stock and accounts on the computer, with a copy in the cloud.
2. **Your local network.** Connect that computer to an ordinary Wi-Fi router. The router does not need an internet connection to do this job. It only needs to be powered on.
3. **Phones and tablets.** Waiters, chefs, bartenders and cashiers connect to the same Wi-Fi, open the browser and go to the computer's address on port 2304, for example `http://192.168.1.15:2304`. Allow port 2304 in the computer's firewall. The number of devices you can use depends on your [plan](/pricing/).
4. **Sync.** When the internet comes back, the till syncs automatically with the cloud, so the web app shows the same sales, stock and reports.

Because orders travel over your own Wi-Fi, an internet outage changes nothing for your team. The kitchen screen still beeps when an order arrives, and the cashier still closes bills and prints receipts. The step-by-step setup is on the [download page](/download/#connect-other-devices).

## What works offline in LoungeOS

On a Windows or Mac till, everything used during service works offline:

- Taking orders at the table or the counter, adding notes and discounts
- Routing food to the kitchen display and drinks to the bar display
- Splitting and merging bills, cancellations with reasons
- Recording cash, card and mobile money payments, and printing receipts on 58 mm or 80 mm printers or as PDF
- Stock levels, out-of-stock blocking and low-stock alerts
- Staff permissions and the activity log
- Sales reports, staff performance and accounting statements

The **web app and the Android app need internet**. For a till that must keep selling through outages, use the Windows or Mac app.

## The 7-day rule and read-only mode

A Windows or Mac till can keep selling without internet for 7 days. After 7 days without syncing, the till becomes **read-only** until it reconnects. A warning shows during the last 2 days, so you have time to connect it.

Read-only means past orders, reports, printing and exports still work, but you cannot make new sales or edits. As soon as the till reconnects and syncs, it works normally again.

The same read-only mode applies when a subscription ends: LoungeOS becomes read-only, on the web and on your tills, until you renew. Nothing is ever deleted.

## Offline-first vs "offline mode": why the difference matters

Cloud POS vendors do offer offline modes, but they come with documented limits. According to their own help centres:

- **Square** lets you take offline card payments, but the session ends after 24 hours until you reconnect. Payments must be uploaded within 72 hours or they expire, and declined offline payments are the seller's loss.
- **Toast** keeps devices working through a local hub. Its documentation says that while offline, staff cannot close checks, reconcile cash and tips or clock out, and reports are delayed until the devices sync.
- **Loyverse** keeps selling offline, but refunds are disabled, stock levels are not shown and integrated card terminals stop working until the connection returns.

These are reasonable designs for markets with reliable internet. In places where connections drop several times a week, a system that *assumes* internet means limits during every outage. We compare them in detail in [Best offline restaurant POS systems](/blog/best-offline-restaurant-pos-systems/).

| | Cloud POS with offline mode | LoungeOS Windows and Mac apps |
|---|---|---|
| Where data lives | Vendor's cloud servers | On your computer, with a copy in the cloud |
| Internet outage | Limited mode, sync later | Keeps selling, syncs when back online |
| Time limit offline | Often hours (24 hours on Square) | 7 days, then read-only until it syncs |
| Reports during outage | Delayed until sync | Available on the till |
| Hardware | Often vendor tablets or terminals | Windows and Mac computers, Android devices, any modern browser |
| Extra devices | Often charged per device | 2, 5 or 10+ devices included in your plan |

## What about power cuts?

No POS can run without electricity, but you can make outages a non-event cheaply:

- Put the **till computer and Wi-Fi router on a small UPS** (inverter). They draw little power, so a modest UPS keeps them running for a long time. A laptop as the till has its own battery.
- Phones and tablets run on their own batteries.
- If your thermal printer is not on the UPS, receipts can wait. Orders still reach the kitchen screen.

Our guide to [running a restaurant during power and internet outages](/blog/run-a-restaurant-during-power-and-internet-outages/) gives a full checklist.

## Your data is kept in two places

On a Windows or Mac till, your data is on the computer and in the cloud. LoungeOS keeps a cloud copy of all your data and makes a full backup every day, so there is nothing to copy to a USB drive by hand. If the computer breaks or is stolen, install LoungeOS on another computer and sign in: everything that has synced comes back from the cloud.

## Frequently asked questions

### How long can LoungeOS run without internet?

A Windows or Mac till keeps selling for 7 days without internet. After 7 days without syncing, it becomes read-only until it reconnects, and a warning shows during the last 2 days. Read-only means past orders, reports, printing and exports still work, but you cannot make new sales or edits.

### Do tablets need mobile data to connect?

Not when they use the Windows or Mac app over your Wi-Fi. They connect to the computer through your router and can have mobile data switched off. Phones and tablets that use the web app or the Android app need internet.

### What happens if the till computer turns off?

Phones and tablets that use it over Wi-Fi cannot reach it until it is back on, so protect it with a UPS. Sales saved on the computer are kept and sync when it is back online. If the computer fails completely, install LoungeOS on another Windows or Mac computer and sign in: everything that has synced comes back from the cloud.

### Can I see my sales from home?

Yes. Sign in to the web app at [app.loungeos.app](https://app.loungeos.app) or the Android app from anywhere with internet. Sales made on a Windows or Mac till appear as soon as it has synced.

### Does the web app work offline?

No. The web app and the Android app need internet. To keep selling during outages, use the [Windows or Mac app](/download/).

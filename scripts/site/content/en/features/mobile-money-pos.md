---
url: /features/mobile-money-pos/
type: feature
title: "POS With Mobile Money: MTN MoMo & Orange Money | LoungeOS"
description: "Create your own payment methods: MTN Mobile Money, Orange Money, cash, card and more. Record transaction references, split bills and reconcile at closing."
h1: "Cash, card and mobile money, recorded properly on every bill"
label: "Payments & Mobile Money"
lead: "In much of Africa, mobile money is how customers pay. In LoungeOS each business creates its own payment methods, such as MTN Mobile Money, Orange Money, cash and card, so every franc is accounted for at closing time."
image: loungeos-pos-order-screen
image_alt: "LoungeOS POS order summary with total ready to charge"
card_title: "Mobile Money & Payments"
card_desc: "Create your own payment methods, MTN MoMo and Orange Money included. Record references and split one bill across methods."
breadcrumb:
  - ["Features", "/features/"]
crumb: "Mobile Money & Payments"
related:
  - /blog/accept-mobile-money-in-your-restaurant/
  - /cameroon/
  - /africa/
---

A POS with **mobile money** support lets the cashier record that a bill was paid by MTN Mobile Money (MoMo), Orange Money or another wallet, with the transaction reference, in the same place as cash and card payments. LoungeOS does this on every plan. Your end-of-day totals then show exactly how much should be in the cash drawer and how much in each wallet.

## Payment methods you create

Each business creates its own payment methods, so the till shows exactly the ways your customers pay. When you create your account, the setup wizard asks which payment methods you accept and creates them for you. You can add, rename or remove them later in your settings.

When the cashier clicks **Charge order**, they pick one of your methods:

- **Cash.** Enter the amount received and LoungeOS shows the change due.
- **Mobile money.** For example **MTN Mobile Money** or **Orange Money**, or any other wallet you created. Type the transaction reference from the confirmation SMS.
- **Card or bank transfer.** For payments on your bank's card terminal or by transfer, with their reference.

A group can **split the payment**, for example part cash and part MoMo. When the payment is confirmed the order is closed, the table becomes available and the receipt prints on your 58 mm or 80 mm thermal printer, or as PDF.

## Why the transaction reference matters

Mobile money fraud at the counter is common. A customer shows a fake or old confirmation message, or a staff member claims a cash sale was paid by MoMo and keeps the cash. Recording the reference on each bill means that:

- At closing, the manager compares LoungeOS mobile money totals with the merchant wallet balance.
- Any payment without a matching reference in the wallet history stands out immediately.
- Every payment is attached to a cashier, a table and a time.

Our guide to [accepting mobile money in your restaurant](/blog/accept-mobile-money-in-your-restaurant/) explains how to set up merchant accounts and a daily reconciliation routine.

## How LoungeOS handles payments

LoungeOS **records** payments. It does not move the money itself. The money moves through the customer's wallet and your merchant account, or through your bank's card terminal. This has two practical advantages:

1. **No extra processing fees from us.** You pay only the operator's or bank's usual fees. LoungeOS takes no percentage of your sales.
2. **Payments don't block service.** Even when the internet is down, a Windows or Mac till can record a cash payment, close the table and print the receipt. Card terminals and mobile money still depend on the operator's network, so record those once the operator confirms.

## Currencies and taxes

The setup wizard asks for your currency and taxes. XAF (FCFA), USD, EUR, GBP, NGN and GHS are built in, and you can add any other currency. Configure your tax rates once, for example VAT at 19.25% in Cameroon, and every bill calculates them automatically.

## Frequently asked questions

### Does LoungeOS connect to the MTN MoMo or Orange Money API?

LoungeOS records mobile money payments with their transaction reference. It does not currently trigger payment requests to the operator. The customer pays to your merchant number or code, and the cashier enters the reference.

### Can one bill be paid with cash and mobile money?

Yes. Split payments let a group pay part of the bill with cash, part with card and part with MTN MoMo or Orange Money.

### Do you charge a fee on mobile money payments?

No. LoungeOS is a flat subscription. Any fees are charged by your mobile money operator or bank, not by LoungeOS.

### Which other wallets can I use?

Any wallet your customers use. Create a payment method for it, for example Wave, Moov Money, Airtel Money or M-Pesa, and it appears at checkout next to your other methods.

### Can I pay for my LoungeOS subscription with mobile money?

Yes. You choose your plan and pay on [account.loungeos.app](https://account.loungeos.app) by Mobile Money (MTN, Orange), card or PayPal. Invoices and receipts are sent by email. See [pricing](/pricing/).

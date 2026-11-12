---
url: /features/restaurant-accounting/
type: feature
title: "Restaurant Accounting Software: P&L & Balance Sheet | LoungeOS"
description: "Record expenses in your own categories, turn sales and stock purchases into double-entry journals, and get a P&L, balance sheet and cash flow."
h1: "Restaurant accounting built into your POS: P&L, balance sheet and cash flow"
label: "Accounting"
lead: "Stop rebuilding your books from receipts at the end of the month. LoungeOS turns every paid order and every stock purchase into balanced journal entries, then produces the three statements your accountant and your bank ask for."
image: loungeos-accounting-dashboard
image_alt: "LoungeOS accounting dashboard with net profit, total revenue, total expenses, profit margin and a revenue versus expenses chart"
card_title: "Restaurant Accounting"
card_desc: "Double-entry journals, P&L, balance sheet and cash flow, generated from your POS and stock data."
breadcrumb:
  - ["Features", "/features/"]
crumb: "Accounting"
related:
  - /blog/restaurant-accounting-basics/
  - /blog/food-cost-percentage-formula/
  - /blog/restaurant-kpis-metrics/
---

Most restaurants run two disconnected systems: a till that knows what was sold, and an accountant who rebuilds the month from receipts, bank statements and notebooks. LoungeOS includes a **double-entry accounting ledger** fed directly by your POS and inventory. Your sales, purchases, expenses and profit are always one click away from being up to date. Expenses and accounting are part of the Business and Pro plans.

## What's included

- **Accounting dashboard** with net profit, total revenue, total expenses, profit margin and a revenue-vs-expenses chart
- **Chart of accounts** in five classes (assets, liabilities, equity, revenue, expenses), with your own sub-accounts
- **Financial journals** listing every entry with reference, date and amount
- **Expenses with categories you create**, such as rent, salaries, utilities, marketing and maintenance. Common categories are made for you when the setup wizard asks for your business type.
- **Three financial statements**: income statement (P&L), balance sheet and cash-flow statement, for any date range, exported to PDF or CSV

## From sale to statement, automatically

Every time a sale is paid, LoungeOS posts its own balanced journal entry, with the order number as the reference. Nobody retypes anything:

- *A paid sale:* debit Cash, Bank or Mobile Money, credit Sales Revenue (and tax if you charge it)
- *A Pay later sale:* debit Accounts Receivable, credit Sales Revenue; the customer's payment then moves it to cash or mobile money
- *A refund:* the reverse of the sale
- *An expense:* debit the expense account, credit where it was paid from

For sales a till made offline, **Sync from the till** in **Journals** posts every sale that has no entry yet. The financial statements update as entries arrive.

Stock written off as damage, waste or loss in [inventory](/features/inventory-management/) is recorded as an expense, so your P&L reflects real losses instead of hiding them.

[[figure:loungeos-financial-reports|LoungeOS financial reports page with profit and loss statement and balance sheet date filters and PDF download|Profit & loss, balance sheet and cash flow for any date range, downloadable as PDF.]]

## Built-in safeguards

- **Debits must equal credits.** LoungeOS will not save a manual journal entry that does not balance.
- **Balance sheet check.** The balance sheet confirms that Assets = Liabilities + Equity.
- **Separation of duties.** The Accountant role has full access to accounting but cannot take orders. Managers can sync and view. See [roles and permissions](/features/loss-prevention/).

## The default chart of accounts

| Class | Example accounts |
|---|---|
| Assets | Cash on hand, bank accounts, inventory |
| Liabilities | Supplier payables, taxes owed |
| Equity | Owner's capital, retained earnings |
| Revenue | Food sales, beverage sales, event services |
| Expenses | Cost of goods, rent, utilities, staff wages, waste and loss |

You can add child accounts under any parent, for example separate accounts for MTN MoMo and Orange Money balances, or for each bank.

## Who it's for

LoungeOS accounting is designed for owners and managers who want to see whether the business makes money, and for accountants who want clean, balanced data instead of a shoebox of receipts. It does not replace your accountant or your local tax filings. It gives them accurate numbers to work from. In OHADA countries, your accountant can map LoungeOS accounts to the SYSCOHADA chart when preparing statutory accounts.

## Frequently asked questions

### Why are my financial statements empty after a busy day?

Each paid sale posts its own entry, so the statements follow the day. If a till sold offline, press **Sync from the till** in **Journals** once it is back online to post those sales, and **Bring the accounts up to date** in Financial Reports refreshes the statements.

### Can I record expenses that don't come from stock?

Yes. Use **Record expense** for rent, salaries, utilities, marketing, maintenance and other costs, with payee, date, payment account and one of your expense categories.

### Can I export statements for my accountant or bank?

Yes. The income statement, balance sheet, cash-flow statement and journal can be downloaded as PDF or CSV for any date range.

### Which plans include accounting?

Expenses and accounting are included in the Business and Pro plans. Starter covers the point of sale, inventory, receipts and daily reports. Every plan starts with a 14-day free trial with Business features, so you can try accounting before you pay. See [pricing](/pricing/).

### Does LoungeOS file my taxes?

No. LoungeOS calculates taxes on bills using the rates you configure and gives you accurate records. Filing remains with you or your accountant.

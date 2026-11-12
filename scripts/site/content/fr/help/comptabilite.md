---
url: /fr/aide/comptabilite/
type: help
lang: fr
section: "Argent et rapports"
order: 2
title: "Comptabilité LoungeOS : journaux, compte de résultat, bilan"
description: "Comment LoungeOS tient vos comptes : écritures automatiques pour les ventes, paiements et dépenses, plan comptable, compte de résultat, bilan et flux de trésorerie."
h1: "Comptabilité : journaux et états financiers"
lead: "Chaque vente, paiement sur compte, remboursement et dépense passe sa propre écriture en partie double. Votre comptable obtient compte de résultat, bilan et flux de trésorerie sans rien ressaisir."
card_title: "Comptabilité et états financiers"
card_desc: "Écritures automatiques, plan comptable, compte de résultat, bilan, trésorerie."
image: loungeos-help-fr-accounting
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/accounting/
related:
  - /fr/aide/depenses/
  - /fr/aide/tableau-de-bord-et-rapports/
  - /fr/logiciel-caisse-restaurant/
---

La comptabilité est incluse dans les formules **Business** et **Pro** (et pendant l'essai gratuit). Les propriétaires, responsables et le rôle **Comptable** y ont accès.

## La vue d'ensemble

**Comptabilité**, **Vue d'ensemble** montre le bénéfice net, le chiffre d'affaires, les dépenses totales et la marge bénéficiaire, chacun comparé au mois précédent, avec les recettes face aux dépenses dans le temps.

[[figure:loungeos-help-fr-accounting|La vue d'ensemble comptable LoungeOS avec bénéfice net, recettes, dépenses, marge et graphique|Chiffres d'exemple. Les dépenses incluent les dépenses enregistrées et le coût du stock vendu.]]

## Les écritures (automatiques)

Ouvrez **Journaux**. Chaque écriture a sa date, son type, sa référence (le numéro de commande), sa description, son montant et son statut. Les onglets filtrent **Toutes les écritures**, le **Journal des ventes**, le **Journal des dépenses** et le **Grand livre général**.

[[figure:loungeos-help-fr-journals|Les écritures LoungeOS avec le chiffre d'affaires de chaque commande|Chaque commande payée passe sa propre écriture ; un paiement sur compte aussi.]]

Ce qui se passe tout seul :

- **Une vente payée** : compte caisse, banque ou mobile money contre ventes (et taxe si vous la facturez).
- **Une vente « Payer plus tard »** : créances clients contre ventes. Le paiement du client la passe ensuite en caisse ou mobile money.
- **Un remboursement** : l'inverse de la vente.
- **Une dépense** : le compte de charge contre le compte d'où l'argent est sorti.

Besoin d'une écriture manuelle (un prêt, un apport du propriétaire) ? Appuyez sur **Nouvelle écriture** ; le débit doit égaler le crédit. La synchronisation depuis la caisse passe les ventes faites hors ligne qui n'ont pas encore d'écriture.

## Les états financiers

Ouvrez **Rapports financiers** :

- **Compte de résultat** entre deux dates.
- **Bilan** à une date : actif, passif et capitaux propres.
- **Flux de trésorerie**.

Chacun se télécharge en PDF, en français ou en anglais, avec votre logo. Si les chiffres semblent courts après un week-end chargé hors ligne, appuyez sur **Mettre la comptabilité à jour**.

## Le plan comptable

**Plan comptable** liste les comptes utilisés par LoungeOS : 1000 Caisse, 1010 Banque, 1020 Mobile Money, 1100 Créances clients, 1200 Stock… et les comptes de charges (5200 Loyer, 5300 Eau et électricité, 5320 Carburant et groupe…). Appuyez sur **Ajouter un compte** pour les vôtres.

[[figure:loungeos-help-fr-chart-of-accounts|Le plan comptable LoungeOS avec les comptes d'actif, de produits et de charges|Ajoutez vos propres comptes si besoin.]]

## Questions fréquentes

### Est-ce un logiciel de comptabilité complet ?

Il couvre ce dont un restaurant, un bar ou une boutique a besoin au quotidien, en partie double, avec des états que votre comptable peut utiliser. Pour les déclarations fiscales et la paie, votre comptable prépare toujours les déclarations ; la paie n'est pas encore dans LoungeOS.

### Pourquoi le bénéfice diffère-t-il des ventes moins les dépenses ?

Le bénéfice retire aussi le coût du stock vendu (d'après le coût unitaire des articles de stock), pas seulement les dépenses enregistrées.

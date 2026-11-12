---
url: /fr/aide/stocks-et-fournisseurs/
type: help
lang: fr
section: "Produits et stocks"
order: 1
title: "Stocks, fournisseurs, réceptions et alertes de stock faible"
description: "Suivez votre stock dans LoungeOS : articles avec unités, coûts et seuils minimum, réception des livraisons, pertes, historique des mouvements et fournisseurs."
h1: "Stocks et fournisseurs"
lead: "Le stock, c'est ce que vous gardez en réserve : casiers, kilos de poisson, sacs de charbon. LoungeOS sait combien il en reste, ce que ça vaut et quand recommander."
card_title: "Stocks, livraisons et fournisseurs"
card_desc: "Articles de stock, réceptions, pertes, mouvements, alertes, fournisseurs."
image: loungeos-help-fr-stock-items
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/stock-and-suppliers/
related:
  - /fr/aide/ajouter-produits-et-categories/
  - /fr/blog/vols-employes-bar-restaurant/
  - /fr/fonctionnalites/
---

Le stock est inclus dans toutes les formules. Le rôle **Gestionnaire de stock** est fait pour la personne qui reçoit les livraisons et compte.

**Produits ou articles de stock ?** Un produit est ce que vous vendez en caisse (une assiette de poisson braisé). Un article de stock est ce que vous achetez et gardez (des kilos de poisson). Les boissons achetées et revendues telles quelles peuvent être des articles de stock vendus en caisse.

## La vue d'ensemble du stock

Ouvrez **Stock**. L'onglet **Vue d'ensemble** montre combien d'articles vous suivez, combien sont en stock faible ou en rupture, la valeur de ce que vous avez, les mouvements dans le temps et la dernière activité.

[[figure:loungeos-help-fr-inventory|La vue d'ensemble du stock LoungeOS avec le total des articles, le stock faible, les ruptures et la valeur|Stock faible compte les articles sous leur seuil minimum.]]

## Ajouter un article de stock

1. Ouvrez l'onglet **Articles** et appuyez sur **Ajouter un article** (ou **+ Nouveau**, **Recevoir du stock** pour une livraison).
2. Remplissez le nom, le SKU, la catégorie, l'**unité** (kg, casier, bouteille, sac…), le stock actuel, le **seuil minimum** et le maximum, le **coût unitaire** et le fournisseur.
3. Facultatif : une photo, un code-barres, et **Vendre en caisse** avec un prix de vente pour ce que vous revendez tel quel.
4. Enregistrez.

[[figure:loungeos-help-fr-stock-items|La liste des articles de stock LoungeOS avec SKU, catégorie, stock, coût, statut et fournisseur|Chaque ligne a Entrée de stock et un menu pour les autres mouvements.]]

## Recevoir une livraison

Pour un seul article, appuyez sur **Entrée de stock** sur sa ligne, tapez la quantité, le coût et une référence (le bon de livraison du fournisseur) et enregistrez.

Pour toute une livraison, appuyez sur **Recevoir du stock** (ou **+ Nouveau**, **Recevoir du stock**) :

1. **Entrée de stock groupée** s'ouvre. Cochez chaque article livré.
2. Appuyez sur **Suivant**, tapez chaque quantité et coût, et une référence comme BC-12345.
3. Appuyez sur **Valider le mouvement**.

[[figure:loungeos-help-fr-stock-receive|La fenêtre Entrée de stock groupée de LoungeOS avec les articles à cocher|Cochez les articles livrés, puis tapez quantités et coûts.]]

## Sorties, pertes et ajustements

Depuis le menu d'un article, enregistrez une **Sortie de stock** (utilisé en cuisine), une **Perte** ou un **Dommage** (avec la raison), ou un ajustement après un comptage. Chaque mouvement est gardé avec qui l'a fait et quand. **Exporter les mouvements** les télécharge pour les dates voulues.

## Alertes de stock faible

Quand un article passe sous son seuil minimum, il passe en **Stock faible**, et **En rupture** à zéro. Vous le voyez :

- dans le cadre **À surveiller** du tableau de bord, avec **Réapprovisionner**,
- sur la vue d'ensemble du stock,
- en notification sur le téléphone du gestionnaire de stock et des responsables.

## Fournisseurs

Ouvrez l'onglet **Fournisseurs** et appuyez sur **Ajouter un fournisseur** : nom, contact, téléphone, e-mail et adresse. Liez les articles de stock à leur fournisseur pour savoir qui appeler quand un article baisse. Les fournisseurs s'importent aussi en CSV.

[[figure:loungeos-help-fr-suppliers|La liste des fournisseurs LoungeOS avec contact et téléphone|Fournisseurs d'exemple.]]

## Questions fréquentes

### Les ventes retirent-elles le stock automatiquement ?

Les produits avec une quantité, et les articles de stock vendus en caisse, sont retirés à chaque vente. Les ingrédients des plats cuisinés s'enregistrent en sortie de stock ou par comptage ; les recettes qui retirent chaque ingrédient ne sont pas encore dans LoungeOS.

### Comment trouver où le stock a disparu ?

Comparez les mouvements avec votre comptage, et vérifiez dans le journal d'activité les ajustements et les pertes. Notre article sur [les vols d'employés en bar et restaurant](/fr/blog/vols-employes-bar-restaurant/) propose une routine hebdomadaire.

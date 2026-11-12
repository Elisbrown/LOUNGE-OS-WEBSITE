---
url: /fr/aide/hors-ligne-et-synchronisation/
type: help
lang: fr
section: "Compte, données et dépannage"
order: 1
title: "Vendre hors ligne et synchronisation LoungeOS (coupures)"
description: "Comment les caisses LoungeOS Windows et Mac vendent sans internet, se synchronisent au retour, l'état de synchronisation et la limite de 7 jours."
h1: "Vendre hors ligne et synchronisation"
lead: "Les caisses Windows et Mac gardent tout sur l'ordinateur et vendent pendant les coupures d'internet. Quand la connexion revient, elles se synchronisent toutes seules."
card_title: "Hors ligne et synchronisation"
card_desc: "Ce qui marche hors ligne, l'état de synchronisation, Synchroniser, la limite de 7 jours."
image: loungeos-help-fr-pos-cart
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/offline-and-sync/
related:
  - /fr/aide/sauvegardes-et-donnees/
  - /fr/blog/coupures-courant-internet-restaurant/
  - /fr/aide/installer-loungeos/
---

## Deux copies de vos données

Chaque commerce a deux copies : une sur chaque caisse Windows ou Mac, et une en ligne. Elles se synchronisent toutes les quelques secondes quand il y a internet. L'application web et l'application mobile travaillent sur la copie en ligne.

## Ce qui marche sans internet

Sur les **applications Windows et Mac**, tout ce qu'il faut pendant le service :

- prendre les commandes, les envoyer aux écrans cuisine et bar, imprimer bons et reçus,
- les paiements avec tous les moyens, les comptes clients (payer plus tard), les remboursements et les validations avec le code PIN d'un responsable,
- le stock retiré à chaque vente, les réceptions de livraisons, les dépenses,
- le tableau de bord et les rapports de ce que cette caisse a enregistré.

Téléphones, tablettes et écrans cuisine peuvent continuer aussi, en ouvrant la caisse dans leur navigateur par votre Wi-Fi (`http://<adresse de la caisse>:2304`, voir la [page Télécharger](/fr/telecharger/#connecter-dautres-appareils)).

Ce qui demande internet : l'application web et l'application mobile, les commandes des clients par QR code, les notifications sur téléphone et les ventes des autres caisses.

## L'état de synchronisation

L'icône nuage en haut de la caisse vous dit où vous en êtes :

- **À jour** : tout est envoyé.
- **Synchronisation…**
- **Hors ligne : les changements restent sur cette caisse**, avec le nombre de changements en attente.
- **Pas encore connectée** ou **Connecter cette caisse** : la caisse n'est pas liée à votre commerce en ligne (voir [Installer LoungeOS](/fr/aide/installer-loungeos/)).
- **Problème de synchronisation** : ouvrez-le pour le détail.

Appuyez sur **Synchroniser** pour envoyer tout de suite au retour de la connexion. Vous n'en avez jamais besoin pendant un service normal.

## La limite de 7 jours

Une caisse qui ne s'est pas synchronisée depuis 7 jours passe en lecture seule : vous voyez tout, mais vous ne pouvez plus enregistrer de ventes jusqu'à la reconnexion. Se connecter une fois, même par le partage de connexion d'un téléphone pendant une minute, suffit à remettre le compteur à zéro. Rien n'est jamais supprimé.

Le même mode lecture seule s'applique quand un abonnement prend fin, jusqu'au renouvellement.

## Coupures de courant

Un ordinateur portable comme caisse tient les coupures courtes sur sa batterie. Avec un ordinateur de bureau, mettez l'ordinateur, le routeur et l'imprimante de reçus sur un petit onduleur. Tout ce qui a été enregistré avant la coupure est gardé sur la caisse.

## Questions fréquentes

### Deux caisses ont vendu la même bouteille hors ligne. Que se passe-t-il ?

Les deux ventes sont gardées, et le stock baisse des deux. La synchronisation ne perd ni n'écrase jamais une vente.

### Puis-je prendre les commandes sur une tablette quand internet est coupé ?

Oui, si la tablette ouvre la caisse dans son navigateur par votre Wi-Fi (`http://<adresse de la caisse>:2304`). L'application web et l'application mobile ont besoin d'internet.

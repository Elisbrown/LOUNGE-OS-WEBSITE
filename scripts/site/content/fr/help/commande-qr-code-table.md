---
url: /fr/aide/commande-qr-code-table/
type: help
lang: fr
section: "Vendre"
order: 6
title: "Mettre en place la commande par QR code à table dans LoungeOS"
description: "Laissez vos clients commander depuis leur table avec un seul QR code : activation, affiche, commandes acceptées ou refusées en caisse. Business et Pro."
h1: "Commande par QR code à table"
lead: "Le client scanne un QR code, voit votre menu avec prix et photos, choisit sa table, ajoute une note et envoie. Le personnel vérifie la commande en caisse avant qu'elle parte en cuisine ou au bar."
card_title: "Commande par QR code à table"
card_desc: "Activer, imprimer l'affiche QR, prendre ou refuser les commandes des clients."
image: loungeos-help-fr-pos-from-tables
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/qr-table-ordering/
related:
  - /fr/aide/tables-et-salles/
  - /fr/aide/application-mobile/
  - /fr/fonctionnalites/commande-qr-code/
---

La commande depuis la table est incluse dans les formules **Business** et **Pro** (et pendant l'essai gratuit). Elle demande que les **Tables** soient activées, et la caisse doit avoir internet pour recevoir les commandes des clients.

## 1. Activez-la

1. Ouvrez **Paramètres de l'entreprise**, **Général**.
2. Sous **Commande depuis la table (QR code)**, activez **Permettre aux clients de commander depuis leur table**.
3. Enregistrez.

[[figure:loungeos-help-fr-config-selforder-on|Paramètres de l'entreprise LoungeOS avec la commande depuis la table activée|Désactivée, le code affiche un message qui invite le client à appeler un membre du personnel.]]

## 2. Imprimez le QR code du menu

1. Appuyez sur **Imprimer le QR code du menu**.
2. Choisissez la langue de l'affiche (**English** ou **Français**) et modifiez le **Titre** et les **Instructions** si vous voulez.
3. Appuyez sur **Imprimer**, ou téléchargez-la en **PDF** ou **PNG** pour l'imprimerie.

[[figure:loungeos-help-fr-qr-poster|L'affiche QR code du menu LoungeOS avec le logo du commerce et les instructions|Un seul code pour tout le commerce, avec votre logo en haut.]]

Il y a un code pour tout le commerce, pas un par table : le client choisit sa table en commandant. Posez-le sur chaque table, sur la carte et au bar. **Nouveau code** désactive les codes déjà imprimés (par exemple si une photo du code a circulé à l'extérieur).

## 3. Ce que voit le client

Pas d'application, pas de connexion. Le client scanne le code avec l'appareil photo de son téléphone :

1. Il voit votre menu avec photos et prix, en français ou en anglais, et ajoute ce qu'il veut.
2. **Voir la commande**, puis **Choisissez votre table** et une note (« poisson bien cuit, s'il vous plaît »).
3. Il envoie et voit **Envoyée au personnel**, puis si elle est acceptée ou refusée.

[[phones:loungeos-help-fr-phone-guest-menu|Le menu client sur un téléphone après le scan du QR code|Le menu;;loungeos-help-fr-phone-guest-cart-filled|La commande du client avec la table choisie et une note|Table et note;;loungeos-help-fr-phone-guest-sent|Commande envoyée au personnel sur le téléphone du client|Envoyée]]

Les clients paient le personnel comme d'habitude à la fin.

## 4. Prenez la commande en caisse

Les commandes des clients arrivent sur toutes les caisses et en ligne sous **Des tables**, avec un compteur et une alerte. Les serveurs qui ont l'application mobile reçoivent une notification.

1. Appuyez sur **Des tables**. Chaque commande montre la table, les articles, la note du client et le total.
2. Appuyez sur **Prendre sur la caisse** : la commande va sur l'addition de cette table. Vérifiez-la puis envoyez-la comme toute commande (stock, bons cuisine et bar et validations fonctionnent comme d'habitude).
3. Ou appuyez sur **Refuser** si vous ne pouvez pas la servir. La page du client l'indique.

[[figure:loungeos-help-fr-pos-from-tables|Commandes des tables dans la caisse LoungeOS avec Prendre sur la caisse et Refuser|Le personnel vérifie chaque commande client avant qu'elle arrive en cuisine.]]

## Questions fréquentes

### Les clients peuvent-ils payer depuis leur téléphone ?

Non. LoungeOS ne traite pas les paiements. Les clients paient le personnel en espèces, mobile money ou carte comme d'habitude, et le caissier l'enregistre.

### Quelqu'un peut-il commander depuis chez lui avec une photo du code ?

Il devrait quand même choisir une table, et le personnel accepte chaque commande avant qu'elle parte. Si cela arrive, appuyez sur **Nouveau code** et réimprimez.

### Ça marche si la caisse est hors ligne ?

La commande du client va sur LoungeOS en ligne : une caisse sans internet ne la reçoit qu'au retour de la connexion. Gardez la caisse en ligne pendant le service si vous utilisez la commande par QR code.

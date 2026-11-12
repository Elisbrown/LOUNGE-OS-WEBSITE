---
url: /fr/aide/paiements-et-recus/
type: help
lang: fr
section: "Bien démarrer"
order: 6
title: "Moyens de paiement, reçus, imprimantes et tiroir-caisse"
description: "Réglez Mobile Money, Orange Money, carte et vos propres moyens de paiement, personnalisez le reçu, branchez l'imprimante 58 ou 80 mm, les bons cuisine et le tiroir."
h1: "Moyens de paiement, reçus et imprimantes"
lead: "Choisissez comment vos clients paient, ce que dit le reçu et où il s'imprime. Chaque caisse peut avoir sa propre imprimante."
card_title: "Paiements, reçus et imprimantes"
card_desc: "Mobile money, moyens personnalisés, reçu 58 ou 80 mm, bons cuisine, tiroir-caisse."
image: loungeos-help-fr-config-receipt
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/payment-methods-and-receipts/
related:
  - /fr/aide/faire-une-vente/
  - /fr/aide/ecrans-cuisine-et-bar/
  - /fr/aide/depannage/
---

Tout se trouve dans **Paramètres de l'entreprise** (la roue dentée en bas du menu latéral). Seuls le propriétaire et les responsables peuvent le modifier.

## Moyens de paiement

1. Ouvrez **Paramètres de l'entreprise**, puis l'onglet **Financier**.
2. Sous **Moyens de paiement**, activez ceux que vous acceptez. Espèces, MTN Mobile Money, Orange Money et Carte sont prêts ; le virement bancaire est là, à activer.
3. Activez **Demander une référence** pour les moyens où le caissier doit taper le numéro de transaction (mobile money, virement). La référence est gardée avec la vente, pour la rapprocher de votre relevé MoMo ou OM.
4. Pour ajouter le vôtre (Wave, une carte de fidélité, un bon d'achat), tapez son nom sous **Nouveau moyen**, choisissez son type et appuyez sur **Ajouter le moyen**.

[[figure:loungeos-help-config-financial|Réglages financiers LoungeOS avec les moyens de paiement Espèces, MTN Mobile Money, Orange Money, Carte et virement|Chaque moyen peut demander une référence.]]

Sur le même onglet, vous réglez la devise, la taxe (seulement si vous la facturez) et les remises que la caisse peut accorder.

## Ce que montre le reçu

Ouvrez l'onglet **Reçu** :

- **En-tête du reçu** : une ligne sous le nom et l'adresse du commerce (« Bienvenue ! »).
- **Lignes en plus** : par exemple votre NIU ou RCCM, avec **Ajouter une ligne**.
- **Pied du reçu** : la ligne du bas (« Merci de votre visite ! »).
- **Afficher qui a servi sur le reçu**, la police et l'interligne.
- **Langue des reçus et des exports** : anglais, français, ou la langue de chaque employé.

L'aperçu à droite montre le résultat pendant que vous tapez, pour le reçu et pour le bon cuisine.

[[figure:loungeos-help-fr-config-receipt|Réglages du reçu LoungeOS avec en-tête, pied, langue et aperçu en direct|Les reçus finissent par « Powered by LoungeOS · loungeos.app ».]]

## Brancher l'imprimante de reçus (application Windows et Mac)

1. Branchez l'imprimante thermique et installez son pilote (Xprinter, Epson et la plupart des imprimantes USB ESC/POS fonctionnent).
2. Dans l'onglet **Reçu**, sous **Imprimante de reçus**, choisissez la **Largeur du papier** : **58 mm** ou **80 mm**.
3. Choisissez l'**Imprimante**, et activez **Imprimer directement sur cette imprimante, sans la fenêtre d'impression** pour des reçus en un geste.
4. Appuyez sur **Imprimer un reçu de test**.

Ces choix d'imprimante sont gardés sur cette caisse dès que vous les faites : chaque caisse peut avoir sa propre imprimante. Dans un navigateur, les reçus ouvrent la fenêtre d'impression : choisissez-y l'imprimante de reçus et mettez les marges à aucune.

## Bons cuisine et bar

Sous **Bons cuisine et bar**, activez **Imprimer les bons cuisine** et **Imprimer les bons bar** et choisissez chaque imprimante (ou **La même que pour les reçus**). À chaque envoi de commande, les plats s'impriment en cuisine et les boissons au bar. Les bons suivants n'impriment que ce qui a changé : articles ajoutés, retirés ou nouvelle note.

## Tiroir-caisse

Un tiroir branché sur l'imprimante de reçus s'ouvre depuis la caisse. Activez **Ouvrir le tiroir après un paiement en espèces** pour qu'il s'ouvre seul, et testez avec **Ouvrir le tiroir maintenant**. Chaque ouverture du tiroir sans vente est notée dans le journal d'activité.

## Questions fréquentes

### Rien ne s'imprime. Que vérifier ?

Sous Windows, ouvrez **Imprimantes et scanners** et vérifiez que l'imprimante n'est pas « Hors connexion » et n'a pas de travaux bloqués. Puis réimprimez le reçu de test depuis Paramètres de l'entreprise.

### LoungeOS prend-il un pourcentage sur les paiements mobile money ?

Non. Vos clients vous paient comme d'habitude. LoungeOS enregistre le moyen, le montant et la référence, et les met dans vos rapports et vos comptes.

---
url: /fr/aide/application-mobile/
type: help
lang: fr
section: "Bien démarrer"
order: 3
title: "L'application Android LoungeOS : notifications et widget"
description: "Installez l'application Android LoungeOS, connectez-vous avec Google, recevez les notifications de votre rôle, ajoutez le widget et scannez les codes-barres."
h1: "L'application mobile LoungeOS"
lead: "L'application Android, c'est tout LoungeOS sur votre téléphone, avec en plus les notifications de votre rôle et un widget d'écran d'accueil avec les chiffres du jour."
card_title: "L'appli mobile : notifications et widget"
card_desc: "Notifications par rôle, widget d'accueil, scan des codes-barres à l'appareil photo."
image: loungeos-help-fr-phone-trio
published: 2026-11-12
modified: 2026-11-12
alternates:
  en: /help/phone-app/
related:
  - /fr/aide/installer-loungeos/
  - /fr/aide/commande-qr-code-table/
  - /fr/fonctionnalites/application-mobile/
---

L'application ouvre le même LoungeOS que sur le web, adapté au téléphone, et ajoute ce que seul un téléphone sait faire : les notifications, un widget sur l'écran d'accueil, l'appareil photo comme lecteur de codes-barres, l'impression et le partage Android.

[[phones:loungeos-help-fr-phone-dashboard|Le tableau de bord LoungeOS sur un téléphone avec les ventes du jour|Le tableau de bord;;loungeos-help-fr-phone-pos|La caisse LoungeOS sur un téléphone avec le menu en plein écran|La caisse;;loungeos-help-fr-phone-kitchen|L'écran cuisine sur un téléphone|L'écran cuisine]]

## Installer et se connecter

1. Sur votre téléphone, ouvrez [loungeos.app/fr/telecharger](/fr/telecharger/) et téléchargez la version Android (Android 7 ou plus récent).
2. Ouvrez **LoungeOS-Android.apk**, autorisez l'installation depuis votre navigateur ou vos fichiers si Android le demande, et appuyez sur **Installer**.
3. Ouvrez l'application et connectez-vous avec votre e-mail et votre mot de passe, ou **Continuer avec Google**. La connexion Google se termine dans le navigateur du téléphone, qui vous renvoie ensuite dans l'application.
4. Autorisez les notifications quand Android le demande.

Si vous aviez l'ancienne application LoungeOS, désinstallez-la après avoir installé celle-ci. Ce sont deux applications différentes.

## Les notifications selon votre rôle

Chacun ne reçoit que ce qui le concerne :

| Événement | Qui le reçoit |
|---|---|
| Un client commande depuis le QR code de la table | Serveurs, caissiers et responsables |
| Un bon arrive en cuisine ou au bar | Le chef (cuisine) ou le barman (bar) |
| Une commande est prête à servir | Le serveur qui l'a prise |
| Une commande est annulée | Les responsables |
| Un article est en stock faible ou en rupture | Le gestionnaire de stock et les responsables |
| Un ticket de support vous est attribué | Vous |

Une notification qui a plus de 10 minutes de retard n'est pas affichée : le téléphone ne se remplit pas de vieilles nouvelles après avoir été éteint.

**Vérifiez que tout marche.** Ouvrez le menu sous votre photo, **Mes paramètres**, **Application mobile**. Vous voyez votre téléphone avec **Notifications activées** ou **Notifications désactivées**. Appuyez sur **Envoyer une notification de test** : elle arrive en quelques secondes. Si elles sont désactivées, autorisez-les pour LoungeOS dans les paramètres Android, puis rouvrez l'application.

## Le widget d'écran d'accueil

Appuyez longuement sur un espace vide de l'écran d'accueil, choisissez **Widgets**, trouvez **LoungeOS** et faites-le glisser. Il affiche jusqu'à quatre chiffres de la journée en cours, choisis selon votre rôle :

- **Propriétaires et responsables** : ventes du jour, nombre de ventes, additions ouvertes, alertes stock
- **Serveurs** : mes ventes, mes additions ouvertes, prêt à servir, commandes des tables
- **Caissiers** : ventes du jour, additions ouvertes, mes ventes, commandes des tables
- **Chefs et barmans** : en attente, en préparation, prêt, en retard (20 min et plus)
- **Gestionnaires de stock** : en rupture, stock faible, articles suivis, valeur du stock
- **Comptables** : ventes du jour, argent encaissé, dépenses, dû sur les comptes clients

Touchez le widget pour ouvrir la page correspondante dans l'application.

## Scanner, imprimer et partager

- **Scanner les codes-barres avec l'appareil photo** : sur la caisse, appuyez sur **Scanner avec l'appareil photo** pour ajouter un produit par son code-barres.
- **Imprimer les reçus** avec l'impression Android, sur toute imprimante que votre téléphone voit.
- **Exports PDF et Excel** (rapports, reçus, listes de stock) : ils ouvrent le menu de partage, pour les envoyer sur WhatsApp ou les enregistrer.

L'application garde votre session ouverte : pas de déconnexion automatique après 30 minutes comme dans un navigateur partagé.

## Questions fréquentes

### Y a-t-il une application iPhone ?

Pas encore. Sur iPhone, ouvrez [app.loungeos.app](https://app.loungeos.app) dans Safari et utilisez **Partager**, **Sur l'écran d'accueil**.

### L'application mobile marche-t-elle sans internet ?

Non. Elle travaille sur votre commerce en ligne. Pour vendre pendant les coupures, utilisez l'[application Windows ou Mac](/fr/aide/hors-ligne-et-synchronisation/) sur la caisse.

### Que collecte LoungeOS depuis l'application ?

Les rapports de plantage, pour corriger les problèmes, marqués uniquement avec vos identifiants d'employé et de commerce (ni nom ni e-mail). Pas d'identifiant publicitaire ni de Google Analytics.

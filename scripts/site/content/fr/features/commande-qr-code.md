---
url: /fr/fonctionnalites/commande-qr-code/
type: feature
lang: fr
title: "Commande par QR code à table pour restaurants et bars | LoungeOS"
description: "Le client scanne un QR code, voit votre menu avec photos et prix, choisit sa table et envoie. L'équipe accepte en caisse. Sans appli, sans commission."
h1: "Commande par QR code à table : le client commande, votre équipe garde la main"
label: "Commande QR code"
lead: "Un QR code sur chaque table. Le client ouvre votre menu sur son téléphone, choisit sa table et envoie la commande. Un serveur l'accepte en caisse et elle part en cuisine et au bar comme toute commande."
image: loungeos-help-fr-pos-from-tables
image_alt: "Commandes des tables dans la caisse LoungeOS, avec Prendre sur la caisse et Refuser"
card_title: "Commande par QR code à table"
card_desc: "Le client commande depuis son téléphone, l'équipe accepte en caisse. Sans appli, sans commission."
breadcrumb:
  - ["Fonctionnalités", "/fr/fonctionnalites/"]
crumb: "Commande QR code"
alternates:
  en: /features/qr-code-ordering/
related:
  - /fr/aide/commande-qr-code-table/
  - /fr/blog/commande-qr-code-restaurant/
  - /fr/logiciel-gestion-bar-lounge/
---

La **commande par QR code à table** permet au client de commander depuis sa table, avec son propre téléphone, sans attendre qu'un serveur le voie. Dans LoungeOS, elle fait partie des formules Business et Pro, et fonctionne avec les tables et les écrans cuisine et bar que vous utilisez déjà.

Elle est pensée pour les terrasses pleines, les lounges le vendredi soir et les restaurants où la deuxième tournée se perd parce que personne n'est passé à la table.

## Côté client

1. Le client scanne le QR code du menu avec l'appareil photo. Rien à installer, aucun compte à créer.
2. Votre menu s'ouvre avec photos, prix dans votre devise et vos catégories, en français ou en anglais.
3. Il ajoute ce qu'il veut, choisit sa table, ajoute une note (« sans piment, s'il vous plaît ») et envoie.
4. Son téléphone affiche **Envoyée au personnel**, puis si la commande est acceptée ou refusée.

[[phones:loungeos-help-fr-phone-guest-menu|Le menu client LoungeOS sur un téléphone après le scan du QR code|Votre menu, avec photos;;loungeos-help-fr-phone-guest-cart-filled|La commande du client avec la table et une note|Table et note;;loungeos-help-fr-phone-guest-sent|Commande envoyée au personnel|Envoyée au personnel]]

## Côté équipe

Les commandes des clients arrivent sur toutes les caisses et dans l'application web sous **Des tables**, avec un compteur et une alerte. Serveurs et caissiers qui ont l'[application mobile LoungeOS](/fr/fonctionnalites/application-mobile/) reçoivent une notification.

Le serveur ouvre la commande, la vérifie et appuie sur **Prendre sur la caisse**. C'est alors une commande normale : elle va sur l'addition de la table, les plats partent sur l'écran cuisine, les boissons sur l'écran bar, et les validations du responsable fonctionnent comme d'habitude. S'il n'y a plus de poisson, le serveur appuie sur **Refuser** et le client le voit aussitôt.

[[figure:loungeos-help-fr-pos-from-tables|Commandes des tables dans la caisse LoungeOS avec la table, les articles, la note et le total|Chaque commande client est vérifiée par une personne avant d'arriver en cuisine.]]

## Pourquoi l'équipe accepte chaque commande

Une commande QR entièrement automatique paraît plus rapide, mais dans un bar elle crée de nouveaux problèmes : un client parti depuis une heure « commande » depuis une photo du code, une table commande deux fois par erreur, un plat épuisé arrive en cuisine. Faire accepter la commande par un serveur coûte un geste et garde la salle sous contrôle. Le serveur reste aussi proche de la table, là où se gagnent les pourboires.

## Un seul code pour tout le commerce

LoungeOS vous donne un QR code pour le commerce, pas un par table. Le client choisit sa table en commandant : vous imprimez une seule affiche et la posez partout, sur les tables, la carte, le bar et l'entrée. Si une photo du code circule là où il ne faut pas, appuyez sur **Nouveau code** et les anciennes affiches ne marchent plus.

[[figure:loungeos-help-fr-qr-poster|L'affiche QR code du menu LoungeOS avec le logo du commerce et les instructions|Imprimez-la depuis l'application, ou téléchargez-la en PDF ou PNG pour l'imprimerie.]]

## Ce qu'elle ne fait pas

- **Le paiement en ligne.** Les clients paient votre personnel comme d'habitude, en espèces, mobile money ou carte. LoungeOS ne prend aucune commission sur vos ventes.
- **La livraison et la vente à emporter depuis chez soi.** Le menu est pour les clients à vos tables.
- **La commande via une caisse hors ligne.** Les commandes passent par LoungeOS en ligne : gardez la caisse connectée pendant le service.

## En place en deux minutes

Activez-la dans **Paramètres de l'entreprise**, **Général**, sous **Commande depuis la table (QR code)**, puis appuyez sur **Imprimer le QR code du menu**. Le guide pas à pas avec captures est dans le centre d'aide : [Commande par QR code à table](/fr/aide/commande-qr-code-table/).

## Questions fréquentes

### Quelles formules incluent la commande QR ?

Business et Pro, ainsi que l'essai gratuit de 14 jours. Voir les [tarifs](/fr/tarifs/).

### Le client doit-il télécharger une application ?

Non. Le menu s'ouvre dans le navigateur du téléphone après le scan.

### Et si un plat est épuisé pendant le service ?

Les produits que vous comptez s'affichent **épuisés** sur le menu client quand ils arrivent à zéro. Pour un plat que vous ne comptez pas, mettez sa quantité à 0 dans **Menu** tant qu'il n'est pas disponible, et refusez les commandes qui le contiennent déjà.

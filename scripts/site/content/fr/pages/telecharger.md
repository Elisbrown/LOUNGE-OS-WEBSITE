---
url: /fr/telecharger/
type: core
lang: fr
title: "Télécharger LoungeOS pour Windows (version 1.3.6)"
description: "Téléchargez le logiciel de caisse LoungeOS pour Windows 10 et 11 : configuration requise, installation, activation de la licence et connexion des tablettes."
h1: "Télécharger LoungeOS pour Windows"
label: "Téléchargement · Version 1.3.6"
lead: "Installez LoungeOS sur un ordinateur Windows, activez l'essai gratuit et connectez vos téléphones et tablettes en Wi-Fi. La plupart des établissements prennent leurs premières commandes en moins d'une heure."
image: loungeos-login-screen
image_alt: "Écran de connexion LoungeOS"
card_title: "Télécharger LoungeOS"
no_hero_cta: true
no_hero_image: true
alternates:
  en: /download/
related:
  - /fr/tarifs/
  - /fr/faq/
  - /fr/fonctionnalites/
---

<div class="download-cards" style="margin-top:0">
  <div class="download-card selected" data-os="windows">
    <h3>Windows</h3>
    <p>Windows 10 et 11 (64 bits) · 383 Mo</p>
    <a href="https://drive.usercontent.google.com/download?id=1eW9bjs97fR2k-I7_yu_kj1p_76zUc3xc&amp;export=download&amp;authuser=1&amp;confirm=t&amp;uuid=ac0c36a6-25cf-46ae-89d9-da18ead345ca&amp;at=AAINaIKicemCbcjo6MrGDzpDD21K%3A1781889497574" class="btn btn-primary">Télécharger LoungeOS 1.3.6</a>
  </div>
  <div class="download-card" data-os="mac">
    <h3>macOS</h3>
    <p>Apple Silicon et Intel · En développement</p>
    <a href="https://drive.google.com/drive/folders/1j5ggnLB0d-j-RQUQOk0hDmwLhpRvts2s" class="btn btn-secondary">Bientôt disponible</a>
  </div>
</div>

Le téléchargement ne démarre pas ? Ouvrez le [dossier de téléchargement LoungeOS](https://drive.google.com/drive/folders/1j5ggnLB0d-j-RQUQOk0hDmwLhpRvts2s) et choisissez la dernière version.

## Configuration requise

| | Ordinateur principal (Windows) | Terminaux (téléphones, tablettes, écrans) |
|---|---|---|
| Système | Windows 10 ou 11, 64 bits | Android, iOS, Windows, macOS |
| Processeur | Intel ou AMD multicœur | Indifférent |
| Mémoire | 4 Go de RAM minimum | Indifférent |
| Stockage | 2 Go libres | — |
| Logiciel | Installateur LoungeOS | Un navigateur web récent |
| Réseau | Relié au routeur Wi-Fi | Même réseau Wi-Fi |

Astuce : un **ordinateur portable** comme poste principal continue de fonctionner sur batterie pendant les coupures de courant.

## Installation

1. Téléchargez **LoungeOS Setup 1.3.6.exe**.
2. Double-cliquez sur le fichier et suivez l'assistant.
3. Ouvrez **LoungeOS** depuis le raccourci du bureau ou le menu Démarrer.

## Activation de la licence (5 minutes)

1. **Créez votre compte** sur [account.loungeos.app](https://account.loungeos.app/sign-up) et choisissez l'essai gratuit ou une formule.
2. **Lancez LoungeOS.** L'écran d'activation affiche un **identifiant machine** (Machine ID).
3. **Copiez cet identifiant** avec le bouton *Copier*.
4. **Générez votre clé de licence** en collant l'identifiant dans votre tableau de bord en ligne.
5. **Collez la clé** dans LoungeOS et cliquez sur **Activer**.

L'activation est la seule étape qui demande internet. Une connexion mobile suffit.

## Première connexion

Connectez-vous avec le compte Super Admin par défaut. Son e-mail et son mot de passe figurent dans la section [connexion d'administration par défaut](/documentation.html#5-default-administration-login) de la documentation (en anglais).

**Changez ce mot de passe immédiatement** dans votre profil, puis créez un compte personnel pour chaque employé. Ne partagez jamais le compte Super Admin.

## Connecter les téléphones et tablettes

1. Branchez l'ordinateur principal et les appareils sur le **même réseau Wi-Fi**.
2. Relevez l'adresse IP locale de l'ordinateur, par exemple `192.168.1.15`.
3. Autorisez le **port 2304** dans le pare-feu Windows.
4. Sur chaque appareil, ouvrez le navigateur et allez à `http://192.168.1.15:2304`.

## Questions fréquentes

### Faut-il installer une application sur les téléphones ?

Non. Les téléphones et tablettes utilisent LoungeOS dans leur navigateur, connectés à l'ordinateur principal par le Wi-Fi.

### Quand la version macOS sera-t-elle disponible ?

La version macOS (Apple Silicon et Intel) est en développement. Écrivez à [hello@loungeos.app](mailto:hello@loungeos.app) pour être prévenu de sa sortie.

### Le message « Database locked » s'affiche. Que faire ?

Une seule instance de LoungeOS doit tourner. Fermez les processus LoungeOS en double dans le Gestionnaire des tâches puis relancez l'application.

---
url: /download/
type: core
title: "Download LoungeOS Restaurant POS for Windows (v1.3.6)"
description: "Download LoungeOS 1.3.6 for Windows 10 and 11. System requirements, installation, licence activation, default login and how to connect tablets on your network."
h1: "Download LoungeOS for Windows"
label: "Download · Version 1.3.6"
lead: "Install LoungeOS on one Windows computer, activate your free trial and connect your phones and tablets over Wi-Fi. Most venues are taking orders within an hour."
image: loungeos-login-screen
image_alt: "LoungeOS login screen on a Windows computer"
card_title: "Download LoungeOS"
card_desc: "Windows 10 & 11 installer, requirements, activation steps and network setup."
no_hero_cta: true
no_hero_image: true
alternates:
  fr: /fr/telecharger/
related:
  - /pricing/
  - /features/offline-pos/
  - /blog/restaurant-pos-hardware-guide/
---

<div class="download-cards" style="margin-top:0">
  <div class="download-card selected" data-os="windows">
    <h3>Windows</h3>
    <p>Windows 10 &amp; 11 (64-bit) · Installer 383 MB</p>
    <a href="https://drive.usercontent.google.com/download?id=1eW9bjs97fR2k-I7_yu_kj1p_76zUc3xc&amp;export=download&amp;authuser=1&amp;confirm=t&amp;uuid=ac0c36a6-25cf-46ae-89d9-da18ead345ca&amp;at=AAINaIKicemCbcjo6MrGDzpDD21K%3A1781889497574" class="btn btn-primary">Download LoungeOS 1.3.6</a>
  </div>
  <div class="download-card" data-os="mac">
    <h3>macOS</h3>
    <p>Apple Silicon &amp; Intel · In development</p>
    <a href="https://drive.google.com/drive/folders/1j5ggnLB0d-j-RQUQOk0hDmwLhpRvts2s" class="btn btn-secondary">Coming soon</a>
  </div>
</div>

Can't start the download? Open the [LoungeOS download folder](https://drive.google.com/drive/folders/1j5ggnLB0d-j-RQUQOk0hDmwLhpRvts2s) and choose the latest version.

## System requirements

LoungeOS installs on **one host computer**. All other devices connect to it through a browser.

| | Host computer (Windows) | Terminals (phones, tablets, screens) |
|---|---|---|
| Operating system | Windows 10 or Windows 11, 64-bit | Any: Android, iOS, Windows, macOS |
| Processor | Intel or AMD multi-core | Any |
| Memory | 4 GB RAM minimum | Any |
| Storage | 2 GB free (for the database and menu photos) | — |
| Software | LoungeOS installer | A modern web browser |
| Network | Connected to your Wi-Fi router | Same Wi-Fi network as the host |

A laptop makes a good host because its battery keeps it running through short power cuts. See our [POS hardware guide](/blog/restaurant-pos-hardware-guide/) for printers, tablets and routers.

## Install on Windows

1. Download **LoungeOS Setup 1.3.6.exe** using the button above.
2. Double-click the file and follow the installation wizard.
3. When it finishes, open **LoungeOS** from the desktop shortcut or the Start menu.

## Activate your licence (5 minutes)

LoungeOS uses a licence locked to your computer.

1. **Create your account** at [account.loungeos.app](https://account.loungeos.app/sign-up) and choose the 30-day free trial or a paid plan.
2. **Launch LoungeOS.** The activation screen shows a unique **Machine ID**.
3. **Copy the Machine ID** with the *Copy* button.
4. **Generate your licence key.** Paste the Machine ID in the licence management panel of your account dashboard.
5. **Apply the key.** Paste the licence key into LoungeOS and click **Activate**.

Activation is the only step that needs internet. After that, LoungeOS runs on your local network.

## First login

After activation, sign in with the default Super Admin account:

- **Email:** sunyinelisbrown@gmail.com
- **Password:** 12345678

**Change this password immediately** in your profile settings, then create personal accounts for every staff member. Never share the Super Admin login with staff. See [roles and permissions](/features/loss-prevention/).

## Set up your venue in four steps

1. **Categories.** Create menu categories and tick *This is a food category* for kitchen items. Leave it unticked for drinks so they go to the bar screen.
2. **Menu items.** Add names, prices, photos (up to 5 MB), available quantities and variations.
3. **Floors and tables.** Create your service areas and tables, and arrange the layout.
4. **Staff.** Add staff with their role. For waiters, assign a floor. Each person sets their own password at first login.

## Connect phones and tablets

1. Make sure the host computer and the devices are on the **same Wi-Fi network**.
2. Find the host's local IP address, for example `192.168.1.15`.
3. Allow incoming connections on **port 2304** in the Windows firewall.
4. On each device, open the browser and go to `http://192.168.1.15:2304` (using your host's IP).

Tip: give the host computer a fixed IP address in your router settings so the address never changes.

## What's new in 1.3.6

- Performance improvements for high-volume service
- Stronger security and more detailed audit logging
- Coming in 1.3.7: more interface languages (currently English and French)

## Frequently asked questions

### Is there a LoungeOS app for Android or iPhone?

You do not need to install an app on phones or tablets. They use LoungeOS through the browser, connected to the host computer on your Wi-Fi. The host itself runs on Windows.

### When will the macOS version be available?

The macOS version (Apple Silicon and Intel) is in development. Follow this page or write to [hello@loungeos.app](mailto:hello@loungeos.app) to be told when it is released.

### Windows Defender warns me about the installer. Is it safe?

Download LoungeOS only from this page or the official download folder. If Windows SmartScreen shows a warning for a new release, choose *More info* → *Run anyway*. Contact [support](/contact/) if you are unsure.

### The app shows "Database locked". What should I do?

Only one copy of LoungeOS should run on the host. Close duplicate LoungeOS processes in Task Manager and reopen the app. See the [knowledge base](/knowledgebase.html) for more troubleshooting.

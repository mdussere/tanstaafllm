# Activités LLM Raspberry Pi

> **Freshness:** 🟢 current · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** wyoh 5 ⏳

> Source : https://chatgpt.com/share/6ac819b6-827c-83eb-93d5-8c1d20e42dfd  
> Export Playwright le 2026-10-09 — 12 messages.

## Utilisateur

Regarde les derniers commits pour te mettre a jour sur le projet

## Assistant

Je suis recalé sur le dépôt GitHub actuel : `mdussere/tanstaafllm`
.

Mais il y a une anomalie : GitHub ne contient actuellement qu’une branche main, dont le dernier commit est 454d437 du 25 septembre. Donc les développements récents sur Wyoh/MCP/WayVNC dont on discutait ne sont pas poussés sur ce dépôt.

Le dernier état visible est :

454d437 — protocole de préparation/revue des commits

864123e — cadrage Wyoh, observabilité desktop et modèle controller-first

0c3addc — cadrage Mycroft / ASR français

6e4e114 — archivage des premières discussions

ac6a473 — charte initiale du projet

Donc je suis maintenant à jour sur GitHub, mais clairement pas sur ton arbre de travail récent. Si tu pensais avoir poussé les commits Wyoh/MCP, ils sont probablement encore sur luna-pi/Termidor ou dans un autre remote/worktree.

## Utilisateur

J'ai pas push
My bad

## Assistant

Ça explique tout 😄. Aucun souci : je reste donc sur notre contexte récent pour Wyoh/MCP/WayVNC, et dès que tu pushes, je pourrai relire les vrais diffs et me synchroniser précisément sur l’état du code.

## Utilisateur

Donc on a réglé le problème de Wi‑Fi. On est resté sur Archer qu'on a modifié. Et là, on est en train de travailler sur l'interface, tous les interacteurs, les boutons, etc. Voilà. On a fait avec Yo, on a avancé sur Swi et l'interface, mais là on est vraiment sur les boutons.

## Assistant

Oui, ça recale nettement l’état du projet.

Je mets donc à jour ma représentation de Luna : le chantier « trouver un OS / faire marcher le hardware » est essentiellement derrière nous. Arch-R reste la base, vous l’avez modifié et le Wi-Fi fonctionne désormais. Donc plus besoin de considérer DarkOS/EmuELEC comme des pistes actives, sauf éventuellement comme références pour les drivers/DTB.

Côté Wyoh, vous avez déjà avancé sur Sway + l’interface, avec l’idée qu’on avait posée : Sway fournit le compositor/WM et son IPC, Wyoh construit la couche de contrôle AI-native au-dessus. Et le chantier actif est maintenant l’interaction physique du R36 Ultra : boutons, D-pad, sticks, triggers, mappings, événements, et leur traduction en primitives d’interaction utilisables par Wyoh.

C’est une étape assez structurante : sur Luna, ces boutons ne sont finalement pas seulement des « touches de gamepad ». Ils deviennent le vocabulaire physique minimal de l’UI, avec Mycroft comme second canal d'entrée. Ça vaut probablement le coup de concevoir l’abstraction des interacteurs avant de figer les mappings bouton → action.

## Utilisateur

Premier pb, il va me falloir un clavier virtuel en plus de la zone de saisie speech to text de Mycroft. En particulier pour les codes wifi ou aitres qui sont difficilement dictables.
Est-ce qu'il y a un clavier virtuel minimaliste q'ou pourrait utiliser.

## Assistant

Oui. Et pour Luna, il y en a un qui semble presque fait exprès pour nous : wvkbd.

wvkbd sur GitHub
 est un clavier virtuel Wayland natif, spécifiquement conçu pour les compositors wlroots, donc parfaitement dans l'écosystème Sway. Le projet se décrit lui-même comme une implémentation volontairement minimale, écrite en C. 
GitHub
+1

Pourquoi je partirais sur wvkbd

Il coche plusieurs cases Luna assez remarquablement :

C, petite codebase : le main.c fait environ 1 300 lignes ; ce n'est pas une grosse stack desktop. 
GitHub

dépendances raisonnables : Wayland, xkbcommon, Cairo, Pango ; le paquet Debian fait ~44 kB compressé et ~793 kB installé sur l'architecture indiquée par Debian. 
Debian Packages

utilise directement virtual-keyboard-v1 + wlr-layer-shell, donc intégration naturelle à Sway. 
GitHub

layouts personnalisables à la compilation.

surtout : on peut le show/hide par signal : SIGUSR1 cache, SIGUSR2 affiche, SIGRTMIN toggle. 
GitHub

Ce dernier point est presque exactement le modèle Wyoh.

Par exemple, un bouton physique pourrait simplement provoquer :

bouton keyboard
      │
      ▼
    Wyoh
      │
      ├── SIGRTMIN ──► wvkbd
      │
      ▼
┌───────────────────────────┐
│ q w e r t y ...           │
│  a s d f ...              │
│    z x c ...              │
│ 123   space   back  enter │
└───────────────────────────┘

Et surtout pas besoin de touchscreen. C'est là que notre usage devient intéressant : on peut probablement forker/modifier wvkbd pour que D-pad/stick déplace le focus, A valide, B efface/retourne, shoulder change de couche, etc.

Pour ton écran 720×720, je ferais même un layout Luna beaucoup plus réduit que mobintl : lettres sur une couche, chiffres/symboles sur une seconde, quelques touches fonctionnelles. wvkbd permet justement de définir ses propres layouts et de sélectionner les couches exposées. 
GitHub

L'autre candidat sérieux est Squeekboard, le clavier de Phosh/Librem 5. Il gère les layouts YAML, DBus, virtual-keyboard-v1, input-method-v2, etc. 
GitHub
 Mais il amène GTK3/Rust et une architecture plus « smartphone Linux ». Pour nos 1 Go de RAM et notre volonté d'avoir des briques très simples que Wyoh peut contrôler, je ne vois pas vraiment ce qu'il nous apporterait de plus.

Donc je testerais wvkbd stock en premier. Et s'il fonctionne correctement avec notre Sway, je pense même qu'un fork Luna/wvkbd adapté aux boutons du R36 pourrait devenir une petite brique de Wyoh plutôt que de développer un clavier de zéro.

## Utilisateur

Est-ce qu'on a un candidat pour la gestion du wifi. Pour l'instant mon ssid et password sont en dur mais si je passe au bureau ça va plus

## Assistant

Oui. Je pense même qu'ici il faut distinguer le moteur Wi-Fi de l'UI Luna.

Mon candidat n°1 serait NetworkManager, piloté par nmcli. Il sait scanner les AP, mémoriser plusieurs profils et leurs credentials, autoconnecter un réseau connu, et créer un profil à la première connexion. 
NetworkManager
+1

L'interface Wyoh peut alors être ridiculement petite :

Wi-Fi
────────────────────
✓ Maison       ████
  Betclic      ████
  Guest        ███
  FreeWifi     ██

       [ Rescan ]

D-pad ↑↓ sélectionne, A connecte. Si le réseau est inconnu, wvkbd apparaît pour saisir le mot de passe. Ensuite NetworkManager conserve le profil et s'y reconnecte automatiquement. Techniquement, Wyoh n'aurait même besoin au départ que de wrapper quelque chose comme :

Bash
nmcli device wifi list
nmcli device wifi connect "$SSID" password "$PASSWORD"

C'est précisément l'usage documenté de nmcli. 
NetworkManager

Et il y a un bonus très intéressant pendant qu'on développe Luna : nmtui existe déjà. C'est l'interface curses officielle de NetworkManager, avec sélection/activation des connexions et édition des profils. 
NetworkManager
 Donc avant même de coder l'écran Wi-Fi Wyoh, on peut avoir un fallback fonctionnel.

Mais vérifions d'abord ce qu'Arch-R utilise déjà

Je ne remplacerais surtout pas la stack réseau maintenant que vous venez enfin de faire fonctionner le Wi-Fi. Il faut regarder ce qu'Arch-R modifié utilise actuellement :

Bash
systemctl status NetworkManager
systemctl status iwd
systemctl status wpa_supplicant
systemctl status connman

Si NetworkManager est déjà là : terminé, on construit l'UI Wyoh autour.

Si c'est iwd, je serais également très tenté de le garder. iwctl fournit déjà scan → liste des réseaux → connexion, et iwd expose son interface via D-Bus. 
Debian Manpages
 C'est potentiellement encore plus séduisant pour Luna en termes de minimalisme.

Donc avant de choisir : donne-moi la sortie de ces quatre systemctl. Vu les contraintes 1 Go de Luna, je préfère qu'on exploite le daemon qui fait déjà marcher ce satané chipset Wi-Fi plutôt que d'ajouter une couche réseau pour le plaisir.

## Utilisateur

Il n'y a pas qq chose de graphique minimaliste ?

## Assistant

Oui — et il y a mieux que nm-applet pour Luna.

Le candidat qui me plaît le plus dépend de ce qui tourne actuellement dessous :

Si votre Wi-Fi fonctionne directement avec iwd : iwgtk. C'est littéralement un frontend graphique léger pour iwd, équivalent graphique d'iwctl : scan, liste des SSID, connexion, réseaux connus, mot de passe, indicateur de signal. 
Debian Packages
 C'est probablement le candidat le plus minimaliste.

Si vous êtes sur NetworkManager : networkmanager-dmenu + wmenu/fuzzel. Ça donne une UI très légère de type launcher : liste des SSID → sélection → saisie du password. Il supporte explicitement Wayland et les nouveaux réseaux protégés. 
GitHub
+1

Il existe aussi nm-sidebar, beaucoup plus proche d'un vrai panneau Wi-Fi moderne Wayland : GTK4, layer-shell, scan, connexion et prompt WPA. 
GitHub
+1
 Mais pour Luna, GTK4/libadwaita me paraît déjà plus lourd que nécessaire.

Un projet récent nommé wifi-manager fait exactement un panneau flottant Wayland/Sway avec NetworkManager, mais il embarque GTK4 + Rust et aussi Bluetooth/audio/etc. : intéressant comme source d'inspiration, moins comme dépendance minimale. 
GitHub

Donc mon choix serait très simple : si Arch-R utilise iwd → essayons iwgtk en premier. Il pourrait carrément être notre écran Wi-Fi V0 sans écrire une ligne de Wyoh.

Et il a un avantage conceptuel important : avec wvkbd + iwgtk, on aurait déjà les deux briques graphiques dont on vient de parler, tout en restant dans Sway :

bouton Wi-Fi → iwgtk → sélection SSID → champ password → wvkbd → connexion.

Ça commence à ressembler exactement à la philosophie Luna : assembler des petits composants Wayland existants, puis seulement remplacer/forker ceux dont l'UX n'est pas adaptée aux boutons du R36.

Here's a quick summary of the conversation:

Le projet utilise Arch-R comme base avec un Wi-Fi fonctionnel sur Archer modifié, et le développement actuel se concentre sur l'interface et les interacteurs physiques (boutons, D-pad, sticks) du R36 Ultra. Un clavier virtuel minimaliste est nécessaire en plus de la saisie vocale, avec wvkbd recommandé pour sa simplicité, intégration Wayland/Sway et possibilités de contrôle via boutons physiques.
Pour la gestion Wi-Fi, NetworkManager piloté par nmcli est privilégié, avec iwd comme alternative légère si déjà en usage. Pour l'interface graphique Wi-Fi, iwgtk est conseillé si iwd est utilisé, sinon networkmanager-dmenu est une autre option légère, permettant une expérience graphique adaptée aux contraintes de Luna et Wyoh.

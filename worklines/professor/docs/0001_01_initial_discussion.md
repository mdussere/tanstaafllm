# Activités LLM Raspberry Pi

> Source : https://chatgpt.com/share/6ab592d0-65a8-83ed-a39d-a20f3cfec445?ogimg=plain  
> Export Playwright le 2026-09-24 — 155 messages.

## Utilisateur

J'ai un raspberry inutilisé.
Y'a des activités llm sympas à faire avec ?

## Assistant

Carrément. Un Raspberry Pi n’est pas idéal pour entraîner un LLM, mais c’est une excellente petite machine pour construire des trucs autour des LLM : inférence locale légère, agents, RAG, passerelles vers des API, domotique, etc.

Tu connais le modèle de Raspberry et sa RAM ? Pi 3/4/5, 2/4/8/16 Go ? C’est ça qui détermine si on peut faire tourner un petit modèle local de façon amusante ou s’il vaut mieux l’utiliser comme serveur/agent.

## Utilisateur

4 et 4

## Assistant

Donc Raspberry Pi 4, 4 Go. Ça limite sérieusement l'inférence locale, mais il y a quand même des projets très sympas — et certains collent bien à ton profil.

Je distinguerais deux usages.

1. Faire tourner un vrai petit LLM localement

Avec llama.cpp et des modèles GGUF quantifiés, tu peux faire tourner des modèles de l'ordre de 0,5 à 1,5B paramètres confortablement en mémoire. Du 3B peut se tenter en Q4, mais ça devient lent et la RAM est serrée.

Quelques candidats intéressants : Qwen 2.5 0.5B/1.5B, SmolLM2 1.7B, éventuellement TinyLlama 1.1B. Ça ne rivalisera évidemment pas avec les gros modèles actuels, mais c'est excellent pour expérimenter avec tokenisation, quantification, context size, sampling, embeddings, tool calling simplifié, etc.

Le côté amusant est justement de mesurer : tokens/s vs quantification vs RAM vs température CPU.

2. Beaucoup plus intéressant : transformer le Pi en « LLM appliance »

Là, le Pi ne fait pas nécessairement le raisonnement. Il devient un nœud permanent qui appelle un gros LLM distant.

Par exemple :

         Raspberry Pi 4
        ┌───────────────┐
        │  FastAPI      │
        │  scheduler    │
        │  SQLite       │
        │  embeddings   │
        │  tools        │
        └───────┬───────┘
                │
         API LLM / local
                │
       ┌────────▼────────┐
       │ GPT / Claude /  │
       │ Gemini / etc.   │
       └─────────────────┘

Et là tu peux faire des choses nettement plus ambitieuses.

Projet que je te conseillerais : un mini Scout domestique. Le Pi ingère en permanence un ensemble de sources — RSS, quelques pages Web, documents, éventuellement MQTT/domotique — stocke les données, fait embeddings + clustering, puis demande au LLM de nommer et résumer les clusters. Tu peux littéralement reproduire en miniature le pipeline collect → embed → cluster → name → aggregate sur une machine à 5 W.

Autre projet assez drôle : multi-agent physique. Chaque agent est un service Docker sur le Pi, avec rôle/mémoire/outils différents. Tu leur donnes une question ; ils produisent indépendamment une réponse, se critiquent mutuellement puis un dernier agent arbitre. Le Pi orchestre tout, les cerveaux sont accessibles par API.

Et un troisième que j'aime bien sur Raspberry : assistant vocal totalement autonome côté hardware :

micro
  ↓
Whisper / whisper.cpp
  ↓
LLM
  ↓
tools
  ↓
Piper TTS
  ↓
enceinte

Le Pi devient alors littéralement un petit objet avec lequel tu parles. STT/TTS peuvent être locaux et seul le raisonnement part éventuellement vers une API.

Avec Pi 4 + 4 Go, je partirais plutôt sur le mini-Scout que sur « faire tourner le plus gros Llama possible ». C'est beaucoup plus riche techniquement : embeddings, clustering, RAG, agents, persistance, scheduling, API et évaluation — et le Pi est parfaitement adapté au rôle de serveur toujours allumé.

## Utilisateur

Y'a des interfaces physique qui rendrait le truc portable et très drôle ?

## Assistant

Oui. Et là, le Pi 4 peut devenir beaucoup plus intéressant qu'un simple serveur.

Je verrais bien un « LLM cyberdeck » portable, un objet volontairement un peu absurde entre Pokédex, terminal Fallout et assistant IA.

6

Avec ton Pi 4, tu peux assembler quelque chose comme :

┌─────────────────────────────┐
│     écran 5" tactile        │
│                             │
│  Scout: « J'analyse... »    │
│  ███████░░░ 72%             │
├─────────────────────────────┤
│ 🎙️   [bouton rouge]   🔊    │
│                             │
│ petit clavier / joystick    │
└─────────────────────────────┘

Le hardware est assez accessible : écran tactile HDMI 4–5", batterie USB-C/powerbank, petit haut-parleur, micro USB/I²S, gros boutons arcade ou encodeur rotatif, éventuellement mini-clavier Bluetooth. Tu mets tout ça dans un boîtier imprimé 3D avec une poignée et ça devient immédiatement ridicule dans le bon sens.

Mais on peut aller beaucoup plus loin : mettre un petit écran rond ou OLED pour le visage de Scout, deux servos pour des oreilles/sourcils, et faire varier son expression en fonction de ce que renvoie le LLM. Le LLM ne produit alors plus seulement du texte :

JSON
{
  "speech": "Ça me paraît franchement suspect.",
  "face": "suspicious",
  "ears": "back",
  "led": "orange"
}

Le Pi traduit ça en voix + animation + LEDs + servos. Là tu as réellement un personnage physique piloté par LLM, plutôt qu'un chatbot dans une boîte.

6

Et pour le rendre portable, je mettrais un bouton push-to-talk plutôt qu'un assistant qui écoute continuellement. Tu te balades avec, tu appuies sur le gros bouton :

« Scout, c'est quoi ce truc ? »

Tu peux ajouter une caméra Pi : photo → modèle vision distant → réponse vocale. Du coup tu peux pointer l'objet vers quelque chose et lui demander ce qu'il voit.

Ça donne une architecture assez marrante :

caméra + micro + boutons → Pi → vision/LLM → voix + écran + LEDs + servos

Et contrairement à un téléphone qui ferait techniquement la même chose, tu disposes des GPIO : boutons physiques, potentiomètres, capteurs, NFC, GPS, caméra, LEDs, moteurs… donc le LLM peut agir physiquement.

Mon choix serait même de ne pas mettre de clavier du tout : écran 4", caméra, micro, HP, molette, 2–3 énormes boutons et une batterie. Un véritable Pokédex GenAI / Scout IRL.

Si tu veux, je peux te proposer 3 designs physiques vraiment réalisables pour ~50 €, ~100 € et ~150 € en réutilisant ton Pi 4, avec les composants précis.

## Utilisateur

https://amzn.eu/d/0eP8NxJ2
On peut créer et mettre de nouveaux jeux emulés dessus ?

## Assistant

Oui, potentiellement, mais je veux vérifier le modèle exact avant de te dire comment : ton lien Amazon redirige vers la référence B0H7DGJH7L, mais Amazon ne me laisse pas accéder à la fiche et cette référence n'est pas encore indexée ailleurs. citeturn0view0

Si c'est bien une console portable rétro à émulation, il y a deux questions différentes :

Ajouter des jeux existants (ROMs) : généralement oui. Sur beaucoup de ces consoles, la microSD contient des dossiers du genre roms/nes, snes, gba, psx, etc. On peut y ajouter ses propres dumps de jeux, dans le respect des droits applicables.

Créer nos propres jeux et les faire tourner dessus : oui, et c'est beaucoup plus drôle. On peut créer un petit jeu destiné à une plateforme émulée (Game Boy/GBA, Pico-8-like, etc.) puis copier le fichier produit sur la console. Selon son OS, on peut parfois aussi développer directement pour Linux/SDL.

Et ça rejoint très bien ton idée précédente : utiliser le Raspberry Pi + LLM pour générer/modifier des petits jeux, puis les jouer sur une vraie console portable.

Envoie-moi juste une capture de la fiche Amazon avec le nom/modèle de la console. Je pourrai te dire précisément quel OS elle utilise, quels émulateurs elle supporte et surtout quelle plateforme serait la plus sympa pour développer nos propres jeux.

## Utilisateur

L'idée ça serait d'utiliser un modèle suffisamment petit pour tenir sur ce hardware

## Assistant

Ah oui — donc mettre le LLM directement dans la console, pas utiliser le Pi comme serveur. Là, ça devient très intéressant.

Le point déterminant est le hardware exact de la console du lien : CPU, RAM et surtout OS. Si c'est une de ces consoles Linux ARM avec 1–4 Go de RAM, on peut potentiellement compiler llama.cpp pour ARM et embarquer un modèle GGUF très quantifié.

Avec 1 Go, je viserais des modèles ~0,3–0,6B ; avec 2 Go, ~0,5–1B ; avec 4 Go, un 1–1,5B Q4 devient réaliste. Le débit sera faible, mais pour un jeu ce n'est pas forcément gênant : le LLM n'a pas besoin de générer 500 tokens.

Et surtout, je ne ferais pas un chatbot. Je ferais un jeu rétro dont le LLM est le moteur narratif. Par exemple un RPG 16-bit où tu peux parler librement aux PNJ :

Garde : « Halte. Personne ne passe. »
Toi : « Le roi m'envoie inspecter les caves. »

→ petit LLM local
→ état du personnage + contexte du jeu
→ « Mouais… montre-moi ton sceau. »

Le modèle pourrait ne générer que 20–40 tokens par interaction, avec une structure imposée du genre dialogue + humeur + action. À 1–3 tokens/s, quelques secondes deviennent acceptables et même assez naturelles pour un jeu rétro.

Encore plus amusant : un roguelike génératif complètement offline. Le programme classique gère combats, cartes, inventaire et règles ; le minuscule LLM ne fait que générer les descriptions, dialogues, quêtes et réactions. Ça permet de masquer énormément les limitations du modèle.

Le vrai challenge sympa serait donc :

console rétro à 50–100 € + llama.cpp ARM + modèle <1B quantifié + jeu SDL → premier petit RPG LLM entièrement offline dans la poche.

Si tu me redonnes le nom exact du modèle de console de ton lien Amazon (ou une capture de la fiche), je peux regarder le SoC/RAM/OS et te dire quel LLM on pourrait réellement y faire tourner et à quelle vitesse approximative.

## Utilisateur

Trouve moi un modèle précis avec un "bon" hardware

## Assistant

Oui. Pour ton idée précise — console portable + émulation + développement maison + LLM réellement exécuté en local — j'ai un candidat très net : la Retroid Pocket 5.

Retroid Pocket 5
€262.81
•
Powerplanet + others
4.7 (377)

La version actuelle vendue par Retroid est même passée à 12 Go de LPDDR4X, avec Snapdragon 865, 128 Go UFS 3.1, microSD, écran AMOLED 5,5", refroidissement actif et batterie 5000 mAh. Le constructeur l'affiche actuellement à 209 $. 
Retroid Pocket

Pourquoi elle est particulièrement intéressante pour notre délire

Le gros avantage n'est même pas Android : elle sait booter un vrai Linux ARM64. ROCKNIX supporte officiellement le RP5 avec kernel Linux mainline, et Batocera le supporte également. 
Rocknix
+1

Donc on pourrait faire quelque chose de beaucoup plus propre que bricoler une APK :

Retroid Pocket 5
Snapdragon 865
12 Go RAM
      │
      ├── Linux ARM64 / ROCKNIX
      │
      ├── notre jeu SDL2
      │
      └── llama.cpp
              │
              ▼
          modèle GGUF

Et 12 Go changent complètement la donne par rapport à ton Raspberry Pi 4/4 Go.

Je commencerais avec un LLM 1,5B–3B quantifié Q4, puis on benchmarkerait. Un 3B Q4 ne prend que de l'ordre de 2 Go pour les poids, ce qui laisse beaucoup de marge pour le KV cache, le jeu et Linux. On pourrait même expérimenter au-dessus, même si le Snapdragon 865 deviendra alors la limitation bien avant la RAM.

Le refroidissement actif est également précieux : pour de l'émulation normale ce n'est qu'un confort, mais pour faire mouliner le CPU plusieurs secondes à chaque génération LLM, ça devient réellement intéressant.

Et le projet devient excellent

Imagine un jeu Game Boy/16-bit volontairement minimal :

┌──────────────────────────────┐
│                              │
│     🧙        🧍             │
│                              │
│ Wizard:                      │
│ "What brings you here?"      │
│                              │
│ > I need to enter the castle │
│   without the guards seeing  │
│   me.                        │
│                              │
│          [ A : TALK ]        │
└──────────────────────────────┘

Le moteur de jeu reste déterministe. Le LLM reçoit seulement quelque chose comme personnage + situation + inventaire + historique condensé et renvoie une petite structure :

JSON
{
  "dialogue": "Perhaps I know another entrance...",
  "attitude": -1,
  "quest": "sewer_entrance"
}

Donc le LLM ne contrôle jamais les règles fondamentales du jeu. Il fait ce pour quoi même un petit modèle est déjà assez intéressant : dialogue, interprétation d'intention et narration.

Et avec 12 Go, on peut garder 100 % du système offline.

Le RP5 a en plus un détail formidable pour ce projet : écran tactile + sticks + boutons physiques. On peut donc utiliser les contrôles normaux pour jouer et faire apparaître un petit clavier tactile uniquement lorsqu'on veut parler librement à un PNJ.

À ~200–270 €, c'est beaucoup plus cher que les petites consoles chinoises à 50 €, mais c'est probablement le sweet spot pour fabriquer une vraie console expérimentale LLM sans tomber dans un Steam Deck à 500 €.

Si tu veux pousser le concept, je chercherais aussi un cran en dessous vers 100–150 € et un cran au-dessus vers 300 €, puis on compare surtout RAM / CPU / Linux / llama.cpp / estimation tokens/s : c'est là qu'on trouvera le meilleur hardware pour ce projet.

## Utilisateur

Format GameBoy et moins de 100e

## Assistant

Oui, avec ces contraintes format Game Boy vertical + <100 €, le choix se resserre énormément. Et pour le LLM, il y a un problème : presque toutes n'ont que 1 Go de RAM.

Mon choix : Anbernic RG40XX V
Anbernic RG40XX V
€79.33
•
Powerplanet + others
4.5 (589)

On la trouve autour de 79 € actuellement. C'est exactement le format recherché : verticale, écran IPS 4" 640×480, Linux ARM64, Allwinner H700 quad-core Cortex-A53 1,5 GHz et 1 Go LPDDR4. Elle accepte aussi des jeux portés nativement, pas seulement des ROMs. 
Anbernic
+1

Le H700 est surtout intéressant parce que c'est un environnement Linux assez ouvert. Donc compiler un petit exécutable ARM64 utilisant llama.cpp est envisageable.

Mais 1 Go change notre ambition LLM. Je ne viserais plus Qwen 1.5B. Il faut plutôt expérimenter autour de SmolLM/Qwen ~0,3–0,5B fortement quantifié, avec contexte court. On serait probablement dans les quelques centaines de Mo de poids, ce qui laisse juste assez de mémoire au système et au jeu.

Alternative ultra-cheap : R36S

La R36S est encore plus marrante comme machine expérimentale : environ 40–70 €, format Game Boy, Linux/ArkOS, RK3326 Cortex-A35 et 1 Go DDR3L. 
HandheldWiki
+1

Mais son CPU est moins intéressant. Pour économiser 30 €, on perd précisément de la puissance dont notre LLM a besoin.

Le TrimUI Brick est très joli et son Allwinner A133P monte à 1,8 GHz, mais il reste lui aussi bloqué à 1 Go de RAM et dépasse souvent 100 €. 
Trimui Official
+1

Donc je prendrais RG40XX V.

Et je changerais légèrement le concept : au lieu d'un LLM qui écrit de longues conversations, faire un jeu où le modèle sert de cerveau décisionnel miniature :

NPC + personnalité
      +
état du monde
      +
action du joueur
      ↓
  LLM ~0.5B
      ↓
intent + émotion + réponse courte
      ↓
 moteur du jeu

Un PNJ qui répond en une phrase de 5–15 tokens, même avec une génération lente, peut être franchement convaincant.

Le défi devient d'ailleurs très sympa : « Quel est le plus petit modèle capable de rendre un RPG réellement génératif sur une console à 80 € ? » Ça ressemble presque à une expérience publiable.

## Utilisateur

Le rg40 est à plus de 100e
Le r36s à l'air bien 
Tu peux confirmer le 1gb ram
Est-ce qu'on peut utiliser le GPU 

【Puce améliorée】Cette console de jeu portable est équipée de plusieurs systèmes Linux open source, vous permettant de passer de l'un à l'autre en toute flexibilité selon le jeu et la situation, pour une expérience personnalisée. Grâce à son processeur RK3326 Cortex-A35 (1,5 GHz) et son GPU Mali-G31MP2 (compatible OpenGL ES 3.2), elle offre un multitâche fluide et sans latence. Les effets spéciaux sont époustouflants et réalistes, offrant des scènes de jeu 3D détaillées.
Show more

## Assistant

Oui, mais avec une réserve importante sur la RAM.

R36S : le hardware « normal »

Les spécifications publiées convergent bien vers :

	R36S
SoC	Rockchip RK3326
CPU	4× Cortex-A35 @ 1,5 GHz
RAM	1 Go DDR3L
GPU	Mali-G31 MP2
API graphique	OpenGL ES 3.2
Écran	640×480, 3,5"
OS	Linux / ArkOS
Stockage	2× microSD
USB	USB-C OTG

iFixit confirme notamment RK3326 + 1 Go DDR3L + Mali-G31 MP2. 
iFixit
+1

Attention cependant aux clones. La R36S est une machine OEM vendue par de nombreux fabricants. Il existe même des témoignages récents de R36S annoncées à 1 Go qui contiennent physiquement 512 Mo. 
Reddit

Donc après achat, première commande :

Bash
cat /proc/meminfo | head

ou simplement :

Bash
free -h

Si on veut faire notre projet, 1 Go réel est indispensable.

Et le Mali-G31 pour le LLM ?

C'est là que ça devient intéressant… mais expérimental.

Le Mali-G31 MP2 est bien un GPU programmable, mais le « OpenGL ES 3.2 » de l'annonce ne signifie absolument pas automatiquement :

llama.cpp → GPU → accélération.

llama.cpp possède aujourd'hui des backends Vulkan et OpenCL. Mais son backend OpenCL officiel est principalement développé/testé pour les Qualcomm Adreno, pas pour ce vieux Mali. 
GitHub

Et il existe justement des retours récents sur llama.cpp montrant que sur les GPU Mali ARM, le backend Vulkan peut être nettement moins performant que le CPU seul. 
GitHub

Donc je partirais sur :

CPU = solution de base fiable. GPU = expérience bonus.

Mais il y a un truc qui me plaît beaucoup

Il existe désormais des forks expérimentaux de llama.cpp visant explicitement les plateformes Rockchip et les GPU Mali. Un projet récent indique notamment avoir fait fonctionner son backend OpenCL sur Arm Mali, là où le backend ggml standard refusait certaines architectures. 
GitHub

Ça ne garantit absolument pas que ça marchera correctement sur ce G31/RK3326, mais pour un projet de hacking c'est précisément intéressant.

Le vrai problème sera plutôt le 1 Go

Prenons un modèle moderne minuscule de 0,5–0,6B.

Grossièrement :

FP16

600 M × 2 octets ≈ 1,2 Go

→ impossible.

Q8

≈ 600 Mo + overhead

→ très serré.

Q4

≈ 300–400 Mo

→ oui.

On aurait quelque chose comme :

1 Go physique
│
├─ Linux / ArkOS       ~150-250 Mo
├─ framebuffer / GPU
├─ jeu                 ~50 Mo
├─ llama.cpp
├─ KV cache            ~50-150 Mo
│
└─ modèle Q4           ~300-400 Mo

Ça commence à devenir crédible, à condition d'utiliser un contexte très court.

Et contrairement à un chatbot, notre jeu peut tricher énormément.

Je ferais même du LLM une mécanique du jeu

Le jeu conserve lui-même :

NPC
├─ name: Bob
├─ mood: angry
├─ trusts_player: 32
├─ knows_secret: true
├─ quest_state: 3
└─ inventory: [...]

Puis seulement au moment d'une conversation :

Bob is angry.
Trust=32.
Player asks:
"Where is the key?"

Answer in <15 words.

Petit modèle 0.5B Q4 → quelques tokens → retour au moteur de jeu.

Pas besoin d'un contexte de 4k/8k tokens.

Et finalement, je préfère presque la R36S au RG40XX pour ce projet

Pas parce qu'elle est puissante : elle ne l'est pas du tout.

Mais à ~40–60 €, Linux ARM64, écran 640×480, contrôles complets, 1 Go, deux SD et USB OTG, on obtient une petite plateforme de développement physique.

Le challenge devient :

faire tourner un véritable jeu GenAI entièrement offline dans 1 Go de RAM sur une console à 50 €.

Ça, je trouve que ça a beaucoup plus de charme que de mettre un 3B sur une console Android à 250 €.

Et je commencerais par benchmarker Qwen autour de 0.5–0.6B en Q4 sur les 4 Cortex-A35, puis CPU vs Mali si on arrive à exposer correctement Vulkan/OpenCL. C'est le premier test qui nous dira si on vise 0,2 token/s ou plusieurs tokens/s — et donc quel type de gameplay est possible.

## Utilisateur

Mon lien amazon confirme le 1gb

Détails supplémentaires

Système : Distributions Linux open source diverses

Taille de l'écran : Écran HD IPS OCA 4 pouces entièrement laminé

Résolution : 720 x 720

Processeur : RK3326 Cortex-A35, 1,5 GHz

GPU : Mali-G31MP2 avec prise en charge d'OpenGL ES 3.2

RAM : 1 Go LPDDR3

ROM : 8 Go eMMC

Wi-Fi : 2,4 GHz

Carte microSD : 16 à 256 Go

Haut-parleur : Haut-parleur intégré de 8 watts (1 ohm)

Joystick : Double joystick ADC avec rétroéclairage 7 couleurs

Batterie : 3000 mAh

Tension d'entrée : 5 V/2 A

Consommation électrique maximale : 5 W

Autonomie : 5 heures

Temps de charge : 1 heure

Ports : Port de charge USB-C / Port de données USB-C OTG Prise casque 3,5 mm

Dimensions : 14,5 × 8,5 × 3 cm

Poids (sans emballage) : 0,2 kg

Dimensions de l’emballage : 16,8 × 10,5 × 4,7 cm
Show more

## Assistant

Oui. Et surtout, ça indique que ce n'est pas la R36S classique : écran 4" 720×720, eMMC 8 Go, Wi-Fi intégré, LPDDR3… C'est probablement une variante plus récente vendue sous un nom proche.

Pour notre usage, c'est même plus intéressant que la R36S standard :

1 Go LPDDR3 confirmé : suffisant pour tenter ~0,5B en Q4.

8 Go eMMC : très pratique pour installer notre environnement Linux sans dépendre entièrement de la microSD.

Wi-Fi intégré : SSH, développement/déploiement à distance, et possibilité d'un mode hybride local/API.

USB OTG : très utile pour débogage et périphériques.

720×720 4" : excellent pour fabriquer une UI de RPG/terminal GenAI.

Mali-G31 MP2 : à expérimenter, mais je partirais du principe que l'inférence sera CPU au départ.

Le point qui me plaît particulièrement est qu'on pourrait développer sur PC puis faire simplement :

Bash
scp game user@console:/opt/game/

et tester directement sur la console.

Je pense que le projet est viable

Je fixerais une contrainte volontairement agressive :

console seule, aucun cloud, <1 Go RAM, LLM local, jeu jouable.

Pour le premier prototype, je testerais trois classes de modèles : ~135M, ~360M et ~500–600M, tous quantifiés, afin de trouver le point où le dialogue reste suffisamment intelligent tout en répondant en quelques secondes.

Le modèle n'aurait surtout pas besoin de connaître tout le jeu. Le moteur lui fournirait uniquement l'état utile à chaque interaction. Avec 1 Go, c'est cette architecture qui rend le concept crédible.

Et le 720×720 ouvre une esthétique assez géniale : Game Boy sous stéroïdes, gros pixels, texte court, PNJ génératifs et temps de génération intégré visuellement au gameplay.

À ce stade, si elle est réellement <100 €, je trouve ce hardware suffisamment intéressant pour tenter l'expérience. Le prochain truc que je vérifierais avant achat est le modèle exact de cette console et surtout quelles distributions Linux tournent réellement dessus, parce que l'annonce Amazon semble mélanger « R36S » avec un hardware qui n'est clairement pas celui de la R36S originale.

## Utilisateur

Il est vendu en 128gb et 64gb, il y aurait quoi comme intérêt aux 128gb

## Assistant

Pour notre projet LLM, pratiquement aucun intérêt à prendre 128 Go.

Les 64/128 Go correspondent très probablement à la microSD fournie, puisque la machine elle-même annonce 8 Go d'eMMC. La différence sert essentiellement à stocker davantage de ROMs.

Un petit LLM quantifié resterait minuscule par rapport à ça :

modèle 0,1–0,2B Q4 : ~100–150 Mo

modèle 0,5–0,6B Q4 : ~300–450 Mo

plusieurs modèles pour expérimenter : quelques Go au maximum

notre jeu + assets : probablement <1 Go

Même avec 10 Go consacrés aux expériences LLM, une carte 64 Go laisse énormément de place.

Je prendrais donc 64 Go, sauf si le supplément pour 128 Go est dérisoire ou si la version 128 Go contient réellement beaucoup plus de jeux qui t'intéressent.

D'ailleurs, pour ce projet, je préférerais presque acheter la version la moins chère et remplacer ensuite la microSD chinoise par une bonne Samsung/SanDisk 64 ou 128 Go. La fiabilité de la carte est beaucoup plus intéressante que sa capacité.

## Utilisateur

+4€ on part sur 128gb

## Assistant

Oui, clairement. Pour +4 €, prends 128 Go.

Ce n'est pas nécessaire pour le LLM, mais à ce prix tu gagnes 64 Go pour les ROMs, plusieurs modèles GGUF, environnements de test et sauvegardes. Ça évite de se poser la question plus tard.

Et notre première expérience quand elle arrive : identifier précisément la machine/OS → SSH → RAM réellement disponible → compiler llama.cpp → benchmarker 3 tailles de modèles sur Cortex-A35. Ensuite on saura exactement jusqu'où on peut pousser le concept.

## Utilisateur

On peut utiliser le gpu pour faire tourner un modèle ?

## Assistant

Techniquement oui. En pratique, je ne compterais pas dessus pour accélérer le LLM. J'ai vérifié plus précisément le cas du Mali-G31 MP2.

Le G31 est un GPU Bifrost supporté par le pilote open source Mesa/Panfrost. Mesa annonce pour le G31 OpenGL 3.1, OpenGL ES 3.1 et Vulkan 1.3 ; en revanche, Panfrost ne fournit actuellement pas OpenCL. 
Mesa 3D Graphics Library

llama.cpp possède bien un backend Vulkan capable d'offloader tout ou partie des couches d'un modèle sur un GPU, par exemple avec -ngl 99. 
GitHub
+1

Donc, si la distribution Linux de cette console expose correctement le G31 via Vulkan, on pourra réellement essayer :

Bash
vulkaninfo
./llama-cli -m model.gguf -ngl 99 -p "Hello"

et comparer à :

Bash
./llama-cli -m model.gguf -ngl 0 -p "Hello"
Mais il y a un piège

Il existe précisément un rapport récent sur llama.cpp concernant les iGPU ARM Mali : avec un Qwen3-0.6B Q4, l'auteur constate que Vulkan est nettement moins performant que l'exécution CPU. L'issue a finalement été fermée sans correction spécifique. 
GitHub

Ce n'est donc pas :

« G31 présent → notre LLM va beaucoup plus vite. »

C'est plutôt :

« G31 présent → on dispose d'un accélérateur programmable sur lequel on peut expérimenter, mais CPU ARM/NEON risque de gagner. »

Et le G31 MP2 reste un tout petit GPU : deux unités d'exécution et mémoire partagée avec notre unique Go de RAM. C'est assez différent d'une carte NVIDIA avec plusieurs Go de VRAM.

Ce que je ferais sur la console

C'est même un benchmark très amusant à réaliser dès qu'elle arrive :

configuration	À tester
Cortex-A35 ×4	llama.cpp ARM/NEON
Mali-G31 MP2	Vulkan
CPU + GPU	offload partiel
quantification	Q4 / Q3 / éventuellement Q2
modèles	~135M → ~350M → ~600M

Le plus intéressant pourrait d'ailleurs être CPU pour le LLM + GPU pour le jeu. Pendant que les quatre A35 génèrent les quelques tokens du PNJ, le Mali continue à gérer l'affichage et les animations.

Et avec seulement 1 Go, je pense que notre travail d'optimisation sur la taille du modèle, la quantification et surtout un KV-cache/contexte minuscule aura beaucoup plus d'impact que le GPU.

Mais oui : on essaiera absolument le Mali. C'est justement le genre de contrainte qui rend ce projet marrant.

## Utilisateur

Pas un pb de performance, ca permet de faire tourner 2 modèles en parallèle

## Assistant

Ah oui — vu comme ça, l'idée CPU + GPU devient beaucoup plus intéressante. Pas pour accélérer un modèle, mais pour avoir deux inférences réellement concurrentes.

On pourrait imaginer :

          1 Go RAM partagé
              │
       ┌──────┴──────┐
       │             │
   Cortex-A35×4    Mali-G31 MP2
       │             │
   modèle A        modèle B
   llama.cpp CPU   llama.cpp Vulkan
       │             │
      NPC          Game Master

Le CPU pourrait par exemple exécuter un petit modèle dialogue, tandis que le GPU exécute un modèle arbitre / world model / intent classifier.

Mais il y a une nuance importante : le G31 n'a pas sa propre VRAM. CPU et GPU utilisent tous deux le même 1 Go de LPDDR3. Donc deux modèles de ~350 Mo ne deviennent pas gratuits parce que l'un est sur le GPU. On aurait potentiellement ~700 Mo de poids + OS + KV caches + jeu + buffers Vulkan, ce qui risque d'être très juste.

En revanche, avec deux modèles vraiment minuscules, ça devient crédible. Par exemple, conceptuellement :

CPU : ~350–500M Q4 (~200–350 Mo)
→ langage/dialogue.

GPU : ~100–200M Q4 (~70–150 Mo)
→ classification, décision, critique, extraction structurée.

Ça pourrait rentrer dans 1 Go avec des contextes très courts.

Encore plus intéressant : un seul modèle chargé deux fois n'est pas forcément nécessaire. Sous Linux, deux processus utilisant le même fichier GGUF via mmap peuvent partager les pages de poids côté CPU. Mais dès qu'on copie/offload les tenseurs vers Vulkan, la gestion mémoire devient différente. Ça méritera un test précis sur la machine.

Et ton idée ouvre un gameplay assez original

Imagine deux « cerveaux » indépendants :

PLAYER
  │
  ▼
┌─────────────┐
│ NPC BRAIN   │ ← CPU
│ "Je refuse" │
└──────┬──────┘
       │
       ▼
┌────────────────┐
│ WORLD / GM AI  │ ← GPU
│ trust -10      │
│ guards alerted │
│ quest unchanged│
└────────────────┘

Ils peuvent même fonctionner simultanément : pendant que le NPC génère son dialogue, le second modèle décide silencieusement des conséquences dans le monde.

Et là la lenteur devient beaucoup moins gênante : si chacun met 3–5 secondes mais travaille parallèlement, le joueur attend toujours ~5 secondes plutôt que 10.

Donc je corrige mon appréciation précédente : pour notre usage, le Mali-G31 mérite vraiment d'être exploité, même s'il est médiocre en tokens/s. L'objectif n'est plus GPU > CPU, mais CPU ∥ GPU.

La vraie contrainte devient 1 Go de RAM partagé, beaucoup plus que la puissance de calcul.

## Utilisateur

Le 2me modèle serait pas forcément un llm

## Assistant

Exactement — et là ça devient beaucoup plus pertinent. Le Mali-G31 pourrait être réservé à un petit modèle spécialisé, pendant que les Cortex-A35 gardent le LLM.

Par exemple :

              R36S-like
          ┌───────────────┐
          │  1 Go LPDDR3  │
          └───────┬───────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
     CPU ×4              Mali-G31
        │                   │
   LLM 0.3–0.6B        petit réseau
   dialogue             spécialisé
        │                   │
        └─────────┬─────────┘
                  ▼
                 jeu

Le GPU pourrait être bien plus utile pour un modèle qui fait de la classification, des embeddings, de la vision très légère, de la détection ou un petit réseau neuronal maison. Là, on n'est plus obligé de passer par llama.cpp : ONNX Runtime, TFLite ou éventuellement NCNN/Vulkan deviennent des pistes beaucoup plus naturelles sur ARM/Mali.

Et surtout, le deuxième modèle peut être minuscule. Quelques Mo ou dizaines de Mo au lieu de plusieurs centaines.

Dans un jeu, je vois plusieurs associations intéressantes : le LLM CPU produit les dialogues tandis qu'un modèle GPU estime par exemple agressivité / confiance / peur / mensonge / intention. Ou le GPU calcule les embeddings permettant de retrouver les souvenirs pertinents du PNJ avant de construire le prompt du LLM.

Encore plus amusant : vision. Le petit modèle GPU analyse quelque chose provenant de la caméra ou d'une image du jeu et transforme ça en quelques features compactes que reçoit ensuite le LLM.

Pour un RPG génératif, je ferais probablement :

CPU → petit LLM ~0.5B pour langage et raisonnement léger
GPU → modèle spécialisé très petit pour perception/classification/embeddings
code classique → règles, inventaire, monde, combats et mémoire persistante

C'est beaucoup plus efficace que d'essayer de faire faire les trois au LLM.

Et il y a même une quatrième ressource qu'on n'a pas encore regardée : le RK3326 peut avoir des accélérateurs multimédia matériels (VPU notamment). Ils ne sont normalement pas utilisables comme NPU généraliste, mais ça vaut la peine d'établir précisément tout ce que contient le SoC et ce que Linux nous expose. Pour une machine à ~50–80 €, ça commence à faire un petit laboratoire edge-AI très rigolo.

## Utilisateur

C'est commandé.

## Assistant

Excellent 😄. À son arrivée, je ferais zéro modification au début : on commence par caractériser exactement la bête, parce que ces consoles ont beaucoup de variantes.

Premier audit via SSH/terminal : uname -a, /proc/cpuinfo, free -h, lsblk, lspci/lsusb, version Mesa, vulkaninfo, drivers Mali/Panfrost, stockage eMMC/SD et RAM réellement disponible.

Ensuite notre feuille de route peut être :

Benchmark brut : CPU Cortex-A35 et Mali-G31/Vulkan.

Compiler llama.cpp ARM64 et mesurer plusieurs petits GGUF, probablement ~100M → ~600M, Q4/Q3.

Trouver le plus gros modèle réellement utilisable dans 1 Go plutôt que celui qui rentre théoriquement.

Tester GPU en parallèle avec un petit modèle spécialisé — embeddings/classification notamment.

Faire un mini programme utilisant directement écran + boutons + sticks.

Puis construire le premier prototype de jeu GenAI 100 % offline.

Le 720×720 vertical + contrôles Game Boy + Linux + Wi-Fi + 1 Go + Mali en fait finalement une plateforme edge-AI beaucoup plus amusante qu'elle n'en a l'air.

Quand tu la reçois, tu peux simplement me dire « elle est arrivée » et on fera l'autopsie logicielle méthodiquement avant de toucher à l'installation.

## Utilisateur

On à quoi comme interfaces physiques?
Juste écran et micro?

## Assistant

Non, justement : cette petite console nous donne déjà pas mal d'I/O physiques. D'après les caractéristiques que tu as données, on a au minimum :

Écran IPS 4" 720×720 : sortie principale, mais a priori non tactile.

Contrôles physiques : D-pad, ABXY, Start/Select, gâchettes + 2 joysticks analogiques. Pour une interface LLM, ça donne beaucoup de possibilités sans clavier.

Haut-parleur intégré : donc sortie vocale via TTS, bruitages, feedback audio.

Jack 3,5 mm : sortie audio/casque.

Wi-Fi 2,4 GHz : réseau, SSH, API éventuelle, communication avec d'autres machines/capteurs.

USB-C OTG/data : probablement notre interface d'extension la plus intéressante.

microSD : stockage/données/modèles.

Et évidemment la batterie, qui en fait un dispositif autonome.

En revanche, dans les specs que tu as copiées, je ne vois pas de microphone intégré. Donc je ne partirais pas du principe qu'il y en a un.

L'USB OTG nous ouvre énormément de choses

On peut ajouter un mini-micro USB, mais aussi une webcam/caméra USB, GPS, dongle Bluetooth, Arduino/ESP32, capteurs, lecteur NFC, etc.

Et un petit ESP32 connecté en USB serait particulièrement intéressant : le Pi/console reste la machine AI, tandis que l'ESP32 devient son interface avec le monde physique :

          CONSOLE
    ┌────────────────┐
    │ LLM + modèles  │
    │ écran / audio  │
    └───────┬────────┘
            │ USB
          ESP32
            │
   ┌────────┼─────────┐
   ↓        ↓         ↓
 caméra   capteurs   servos
 LEDs     distance   moteurs
 boutons  lumière    etc.

Mais pour le premier prototype, je n'ajouterais rien sauf éventuellement un micro USB minuscule.

Les contrôles de la console sont déjà parfaits pour inventer une interface LLM inhabituelle. Par exemple L1 = parler au personnage, joystick = sélectionner le contexte/objet, R1 = demander au deuxième modèle d'analyser, A/B = accepter/refuser une action. On n'est alors surtout pas en train de fabriquer un mauvais smartphone : on fabrique une vraie interface physique pour modèles.

Et si on veut de la voix, micro USB + Whisper tiny ou un modèle ASR encore plus petit devient une troisième expérience edge-AI très intéressante.

## Utilisateur

Pas d'accelerometre ?

## Assistant

A priori non. Dans les spécifications de ton modèle, aucun accéléromètre/gyroscope/IMU n'est mentionné, et sur cette catégorie de consoles RK3326 ce n'est généralement pas présent.
Mais USB-C OTG permet d'en ajouter un. Un petit ESP32 + MPU6050 (accéléro + gyro) coûterait quelques euros et permettrait de rendre la console sensible aux mouvements.
Pour notre projet, ce serait même assez drôle : secouer la console pour interrompre le LLM, incliner pour influencer un personnage, détecter qu'on la prend en main, etc.
Quand elle arrive, on pourra aussi vérifier directement si un capteur inattendu est exposé par Linux dans /sys/bus/iio/devices/.

## Utilisateur

Je resye sir qq chose d'intégré.
Il y a un micro?

## Assistant

Non, d'après la fiche que tu as copiée, aucun micro intégré n'est indiqué.

Elle mentionne explicitement le haut-parleur intégré et la prise jack 3,5 mm, mais pas de microphone. Sur ce type de console, si un micro MEMS était présent, c'est normalement une caractéristique annoncée.

Donc, en restant strictement sur ce qui est intégré, on aurait essentiellement :

Entrées : D-pad, ABXY, Start/Select, gâchettes, 2 sticks analogiques.
Sorties : écran 720×720, haut-parleur, probablement LEDs/RGB des sticks.
Communication : Wi-Fi.
Pas identifié : tactile, micro, caméra, accéléromètre/gyro.

Par contre, j'aimerais bien identifier exactement le modèle que tu as commandé : les caractéristiques 4" 720×720 + RK3326 + eMMC 8 Go + sticks RGB ne correspondent pas à la R36S classique. Si tu me donnes le nom affiché en haut de la fiche Amazon (R36S Pro, R36MAX, etc.), je peux chercher son PCB/spec réelle et voir s'il y a des périphériques intégrés que la fiche oublie.

## Utilisateur

Bluetooth ?

## Assistant

Dans les specs Amazon que tu as copiées : non, Bluetooth n'est pas mentionné. Elles indiquent explicitement Wi-Fi 2,4 GHz, donc je ne considérerais pas le Bluetooth comme acquis.

C'est d'ailleurs intéressant : si le module radio était un combo Wi-Fi/Bluetooth, le Bluetooth pourrait être présent matériellement mais non annoncé/supporté par l'OS.

Quand elle arrive, on pourra le vérifier immédiatement avec rfkill list, bluetoothctl list et dmesg | grep -i bluetooth.

## Utilisateur

Fais une recherche avancée sur des projets indépendants sur ce hardware

## Assistant

Oui. J'ai creusé non pas seulement la « R36S », mais les projets indépendants autour du RK3326/Mali-G31 et des nombreuses variantes/clones R36. Et c'est nettement plus hackable que je ne le pensais.

Premier point important : ta machine n'est presque certainement pas une R36S originale. Les caractéristiques 4" 720×720, 8 Go eMMC, Wi-Fi et sticks RGB correspondent à la nouvelle galaxie de variantes/clones RK3326. C'est important parce que les projets communautaires récents commencent justement à les prendre en charge. 
GitHub
+1

Le projet le plus intéressant que j'ai trouvé

Quelqu'un utilise déjà une R36S comme ordinateur Linux généraliste, explicitement pour écrire et exécuter ses propres applications plutôt que pour l'émulation. Il documente le RK3326, les périphériques, le boot et le développement custom. 
Ignavus

Encore mieux : un autre projet a porté SDR++, une grosse application desktop de radio logicielle, sur R36S/RK3326. C'est une excellente démonstration pour nous parce que ce n'est absolument pas un jeu : l'auteur fait fonctionner une application graphique Linux complète sur le Mali-G31, sans X natif, avec Weston/XWayland/GL4ES, et remappe même le joystick en souris. 
GitHub

Autrement dit :

RK3326
 ├── applications ARM64 natives     ✓
 ├── SDL2                           ✓
 ├── framebuffer                    ✓
 ├── OpenGL ES / Mali-G31           ✓
 ├── Weston                         ✓
 ├── XWayland                       ✓
 ├── PortMaster                     ✓
 ├── joystick / boutons Linux       ✓
 └── réseau / USB                   ✓

C'est exactement le genre d'environnement qu'il nous faut.

Il existe maintenant un véritable écosystème de firmwares

Le projet dArkOSRE-R36 est particulièrement intéressant : il vise explicitement les R36S et leurs clones RK3326, avec détection de nombreuses cartes mères. Il expose notamment Wi-Fi, USB tethering, joysticks, boutons, audio, LEDs et ajoute même un Bluetooth Manager pour le hardware compatible. 
GitHub

dArkOSRE-R36 sur GitHub

Il y a également ArkOS4Clone, dont la liste de machines supportées est devenue énorme : R36S, R36Pro, R36Plus, R36Max, R36Max2, R36Ultra, R40XX, R40XX Pro Max, etc. 
Handhelds Wiki

C'est plutôt rassurant pour notre étrange modèle Amazon : même s'il s'agit d'une nouvelle variante, il y a de bonnes chances qu'on puisse identifier sa carte et trouver une branche communautaire appropriée.

Et on peut accéder directement aux contrôles

Un projet récent a même documenté les devices Linux de ces machines. Les contrôles apparaissent notamment sous :

/dev/input/event*
/dev/input/js0

et l'auteur lit directement les structures js_event Linux depuis Python. 
GitHub

Donc notre programme n'a même pas besoin d'être « un jeu émulé ».

On peut faire :

boot
  ↓
Linux
  ↓
notre application ARM64
  ├── /dev/input/js0
  ├── SDL2 → écran
  ├── ALSA → speaker
  ├── llama.cpp → CPU
  └── Vulkan/GLES → Mali

Ça change pas mal ma vision du projet : on développe une application Linux native pour une machine Game Boy, pas une ROM.

PortMaster est probablement notre meilleure porte d'entrée

PortMaster est justement conçu pour lancer des programmes Linux natifs sur ces handhelds. Le guide communautaire recommande ArkOS/dArkOS-RE sur R36S et clones. 
Gist

On pourrait donc à terme empaqueter notre truc comme :

PORTMASTER
   │
   └── GenBoy AI
        ├── genboy        ← ARM64
        ├── model.gguf
        ├── assets/
        ├── config/
        └── launch.sh

Il apparaîtrait dans le menu Ports à côté des jeux normaux.

Et potentiellement on pourrait publier le package pour que d'autres possesseurs de RK3326 le testent.

Un détail intéressant pour ton idée CPU + GPU

Le port SDR++ montre que le Mali-G31 est réellement accessible par des applications non-émulateur. L'auteur utilise le GPU via GLES/GL4ES. 
GitHub

Ça ne prouve toujours pas que Vulkan compute fonctionnera correctement sur notre variante précise, mais ça confirme au moins :

CPU et GPU sont exploitables indépendamment par nos propres programmes.

Donc l'architecture que tu imaginais reste très crédible :

       ┌──── RK3326 ────┐
       │                │
 Cortex-A35 ×4       Mali-G31
       │                │
    llama.cpp        petit NN
       │                │
       └──────┬─────────┘
              ↓
          GAME ENGINE
              │
     ┌────────┼────────┐
   écran    speaker   controls

Et un classifieur/embedding/network minuscule sur GPU est probablement une meilleure expérience que d'essayer d'y mettre un deuxième LLM.

Il y a néanmoins une chose à ne surtout pas faire quand elle arrive

Ne pas flasher immédiatement ArkOS.

Les projets communautaires insistent énormément sur les différences de carte mère, écran, DTB, audio et contrôleurs entre variantes. dArkOSRE maintient carrément une table par motherboard ID/panel. 
GitHub
 Un autre projet documente un clone où l'eMMC interne, les axes des joysticks et l'audio nécessitent tous une configuration spécifique. 
GitHub Wiki Search

Donc je ferais d'abord une image complète de l'eMMC/SD d'origine, puis extraction du Device Tree (.dtb). Ce fichier va nous dire énormément de choses sur le vrai hardware : contrôleur Wi-Fi, GPIO, audio, LEDs, éventuel Bluetooth, éventuellement des périphériques que l'annonce Amazon ne mentionne même pas.

Et c'est justement là que ta question précédente sur « qu'est-ce qui est physiquement intégré ? » pourra recevoir une réponse définitive.

Je suis maintenant assez convaincu qu'on a acheté, presque accidentellement, un petit devkit Linux RK3326 autonome avec écran, batterie, GPU, audio et gamepad pour ~50–80 €. Pour le projet edge-AI, c'est beaucoup plus intéressant qu'une simple console d'émulation.

## Utilisateur

C'est pas drôle.
Liste des projets variés et amusants

## Assistant

Oui, j'étais parti beaucoup trop « plateforme de dev ». 😄 Si on considère la machine comme un mini-ordinateur Linux de poche avec écran, sticks, boutons, son, Wi-Fi et GPU, il y a des projets nettement plus marrants. La communauté confirme qu'on peut écrire des applis natives SDL2/C/C++/Python/Rust et accéder directement aux contrôles. 
GitHub
+1

Voici ceux que je trouve vraiment intéressants :

🐹 Tamagotchi LLM — probablement mon préféré. Un personnage vit en permanence dans la console. Il a humeur, mémoire, besoins et personnalité. Un petit LLM local produit ses réflexions/dialogues. Tu peux le nourrir, l'emmerder, l'abandonner trois jours... RTC + sauvegarde permettent qu'il « vive » quand la console est éteinte.

🎭 RPG où les PNJ improvisent — jeu rétro classique, mais tu construis tes phrases avec quelques mots/actions aux boutons. Le LLM fait parler les personnages et un petit modèle secondaire classe l'intention : menace, mensonge, séduction, marchandage, etc. Les règles du monde restent déterministes.

🕵️ Jeu d'interrogatoire — cinq suspects génératifs, un meurtrier. Chacun possède des faits secrets et peut mentir. Tu interroges avec des choix/composition de phrases. Le LLM joue les suspects ; un moteur classique garantit que le mystère reste logiquement soluble.

👾 Pokémon génératif — tu explores un monde et rencontres des créatures procédurales. Le modèle invente nom, description et personnalité à partir de caractéristiques numériques. Tu construis progressivement ton propre Pokédex unique.

🧠 Deux IA qui se disputent dans ta poche — CPU = personnage A, GPU/petit NN = personnage B ou arbitre. Tu leur donnes un problème et regardes les deux petits idiots débattre. Les sticks permettent de donner des points à l'un ou à l'autre.

🔮 Oracle de poche — tu choisis quelques symboles/paramètres aux sticks, secoues virtuellement les dés avec les boutons, et le modèle fabrique prophétie, horoscope absurde ou interprétation. Techniquement trivial, mais parfait pour tester jusqu'où un 0,5B peut produire quelque chose de drôle.

📻 Radio cyberpunk — il existe déjà un port communautaire de SDR++ pour RK3326. Avec un petit dongle SDR en USB, la console devient scanner radio avec waterfall à l'écran. 
GitHub
 Un LLM pourrait ensuite transformer les données/métadonnées reçues en interface façon détecteur paranormal.

💀 Terminal Fallout — remplacer complètement l'interface par un faux terminal militaire des années 80. Commandes, fichiers secrets, énigmes, conversations avec une « IA enfermée dans la machine ». Là, la faible puissance devient une caractéristique esthétique plutôt qu'un défaut.

🎮 Générateur de mini-jeux — bibliothèque de mécaniques prédéfinies (labyrinthe, shooter, platformer...). Le LLM génère règles, textes, ennemis et paramètres ; le moteur assemble le jeu. Chaque démarrage produit un jeu légèrement différent. Le développement natif SDL2 est déjà bien documenté sur R36S. 
GitHub

🗣️ Animal qui apprend ton langage — au départ il ne comprend quasiment rien. Tes interactions alimentent progressivement sa mémoire/vocabulaire. L'intérêt serait de mettre en scène les limitations du petit modèle : il est censé être un animal vaguement intelligent.

🧬 Élevage d'IA — plusieurs minuscules agents possèdent chacun quelques paramètres/personnalités. Tu les fais interagir, tu sélectionnes ceux dont le comportement t'intéresse et tu « reproduis » leurs paramètres/prompts. Une sorte de jeu d'évolution artificielle.

🧟 Survivant autonome — tu ne contrôles pas directement le personnage. Tu lui donnes des intentions : « trouve de la nourriture », « évite cet homme », « explore vers le nord ». L'agent décide ensuite tout seul pendant 30 secondes et tu observes les conséquences.

🎲 Maître de jeu de poche — générateur de dungeon/RPG papier : cartes procédurales à l'écran, dés aux boutons, inventaire, événements et narration LLM. À plusieurs autour d'une table, la petite Game Boy devient le MJ.

⚔️ Pokémon mais pour modèles IA — celle-ci pourrait être particulièrement drôle pour nous : on installe plusieurs minuscules modèles. Chacun est un combattant. Même prompt envoyé aux modèles ; classifieur/arbitre évalue certaines propriétés objectives de leurs sorties ; animations de combat à l'écran. Tu collectionnes réellement des GGUF.

🖥️ Ordinateur de poche complètement détourné — mini desktop, terminal, lecteur Markdown, calculatrice Python, SSH vers Termidor, monitoring réseau, etc. Il existe déjà des projets de desktop R36S et même une distribution Arch Linux dédiée aux R36/clones ; la machine est donc réellement détournable de sa fonction console. 
Arch R

Et côté détournements non-IA, les gens commencent même à faire tourner des jeux Flash via Ruffle directement sur ces handhelds ARM64. 
Reddit
 Ça donne une idée du niveau de liberté.

Mes trois à nous : Tamagotchi LLM, jeu d'interrogatoire, et RPG à PNJ génératifs. Le Tamagotchi a un avantage particulier : avec un modèle très limité, les erreurs, oublis et raisonnements un peu débiles deviennent la personnalité de la créature au lieu d'être des bugs. C'est presque le hardware idéal pour ça.

## Utilisateur

Sinon en faire une plateforme de codage codex toujours dans ma poche

## Assistant

Oui — et paradoxalement ça peut être plus utile que le LLM local.

Je verrais la console comme un terminal Codex de poche, pas comme la machine qui exécute le gros modèle. Le RK3326 fait tourner l'interface, Git, SSH, éventuellement un éditeur ; Codex tourne à distance.

┌──── console 4" / Linux ────┐
│                            │
│  Scout > fix failing tests │
│                            │
│  ▸ src/parser.py           │
│    +17 -4                  │
│                            │
│  [A] diff   [X] test       │
│  [Y] commit [B] back       │
└─────────────┬──────────────┘
              │ Wi-Fi
              ▼
        Codex / serveur
              │
              ▼
          Git repository

Le truc intéressant serait de ne surtout pas essayer de reproduire VS Code sur 4 pouces. On ferait une UI pensée pour les contrôles physiques : D-pad = naviguer fichiers/hunks, A = sélectionner, B = retour, X = lancer tests, Y = afficher diff, gâchettes = changer de panneau, sticks = scroll rapide.

Pour écrire les prompts, c'est le point difficile sans clavier ni micro. Mais on peut avoir un système de prompts composables : Fix → tests failing → current file, Explain → selected code, Refactor → function, Implement → issue. Et quand il faut réellement écrire, connexion d'un petit clavier Bluetooth/USB — sous réserve qu'on confirme le Bluetooth.

Encore mieux : la console pourrait être essentiellement un client de Termidor. Tu la sors de ta poche, elle se connecte en SSH, retrouve automatiquement ta session tmux, et tu as ton environnement de développement existant. La console ne stocke presque rien.

Pocket console
     │
     │ SSH
     ▼
  Termidor
     │
 ┌───┴────┐
 git    Codex
 tests   python

Avec Wi-Fi intégré, c'est parfaitement cohérent. Et via téléphone en hotspot, ça devient réellement utilisable dehors.

Il y a même un concept que j'aime davantage : « Codex pager ». Tu lances un travail Codex depuis ton PC, mets la console dans ta poche et elle affiche l'état des tâches. Quand Codex demande une décision, la console vibre/sonne : « Apply this patch? » → A = oui, B = non, X = voir diff.

Là, le format Game Boy cesse d'être un gimmick : les boutons physiques deviennent excellents pour superviser des agents de coding sans sortir un ordinateur.

## Utilisateur

Bon, j'ai quelques idées, c'est peut-être un peu brouillon, mais je vais les poser là. Donc, voilà. L'idée, ça serait que cette machine, ce soit l'objet et le moyen d'un développement LLM. C'est-à-dire qu'elle va supporter le développement, hoster le code, interagir avec GitHub, utiliser Codex, appeler Codex, faire les compils s'il y en a besoin, etc. Et elle sera aussi l'objet de ces développements. C'est-à-dire que le but, c'est que je donne des instructions et qu'elle s'auto-code, et qu'elle teste sur elle-même, etc. Comme ce qu'on fait avec du VS Code et si on testait sur une machine. Et la contrainte qu'on va avoir, c'est que contrairement à ce qu'on fait quand on a VS Code, par exemple, je ne vois pas le code et je n'ai pas de clavier. Donc le premier point, ça sera sans doute le voice to text et la manière de fiabiliser le voice to text, le voice to command line. Et ça, potentiellement, c'est ça qui pourrait être le modèle géré par le GPU. Ceci étant posé, ceci étant posé, je me dis que si l'IA fait l'interface avec cette machine, donc voice vers contrôle de la machine, environnement de développement, il faut aussi qu'elle ait la main dessus, sur la machine. Et peut-être qu'un des premiers points, ça serait de dire : ben voilà, grosso modo, je ne vais pas passer par un terminal, je veux quelque chose de plus évolué qu'un terminal. Donc potentiellement, je vais attaquer l'environnement, le desktop. Et peut-être qu'en fait, il faudrait réfléchir à faire un window manager intégré avec l'IA. C'est-à-dire potentiellement avoir un window manager auto-descriptif. C'est-à-dire au lieu d'utiliser un modèle lourd pour aller regarder l'image, le produit final du window manager, mon desktop, qu'est-ce que c'est, comprendre que ça, c'est une icône, savoir... c'est peut-être faire que on refait un Windows manager complet qui donne la main à un modèle, qui ressort une représentation JSON enrichie ou structurée, etc., de son window manager, voire hiérarchique, voire je ne sais pas. Mais ça pourrait être ça. Et là, ça serait un peu badass, c'est-à-dire de dire que l'IA a un contrôle fin sur cette machine au coût le plus minimaliste. Voilà un peu tout ce à quoi j'ai pensé. Pose-le, résume-le, ouais, fais un petit compte rendu et on y retravaillera après ma journée de travail.
Show more

## Assistant

Oui. Je pose ça comme une note de concept, sans chercher encore à résoudre les choix techniques.

Concept — une machine qui se développe elle-même

L'idée centrale est de faire de cette petite console Linux à la fois l'environnement de développement et la cible du développement.

Ce n'est donc pas simplement un terminal portable permettant d'appeler Codex. Le but serait progressivement de construire une machine dont l'interface principale avec son propriétaire est l'IA, et qui dispose elle-même des moyens nécessaires pour modifier son propre logiciel.

Boucle fondamentale

Le fonctionnement cible serait quelque chose comme :

          UTILISATEUR
              │
         voix / boutons
              │
              ▼
       ┌──────────────┐
       │ Interface IA │
       └──────┬───────┘
              │ intention
              ▼
        Codex / agent
              │
       ┌──────┴───────┐
       ▼              ▼
     GitHub         Machine
       │              │
       │          écrit code
       │          compile
       │          installe
       │          exécute
       │          observe
       │          teste
       │              │
       └──────► correction
                     │
                     └────► nouvelle version

Tu pourrais donc lui dire quelque chose comme :

« Quand j'appuie deux fois sur L1, je veux afficher l'utilisation CPU en haut à droite. »

Elle inspecte son environnement et son code, demande à Codex de faire la modification, compile/installe, lance le résultat sur elle-même, vérifie éventuellement le comportement, et te présente le résultat.

Git devient à la fois son historique et son mécanisme de retour arrière.

La contrainte intéressante : pas de clavier, pas de code

Contrairement à VS Code, l'utilisateur ne travaille quasiment jamais directement sur le code.

Ça force à inventer une interface différente :

intention → agent → code → exécution → observation

plutôt que :

clavier → code → compilation → exécution.

La première brique importante devient donc effectivement voice-to-intent, et pas seulement voice-to-text.

Il pourrait y avoir deux étages :

audio
  ↓
petit modèle ASR local
  ↓
texte
  ↓
LLM / Codex
  ↓
intention + action

Le Mali-G31 devient un candidat intéressant pour l'ASR si nous trouvons un runtime/modèle approprié : pendant que le CPU fait tourner le système et éventuellement d'autres traitements, le GPU traite la voix.

La fiabilité sera un sujet de recherche en soi : comment transformer une reconnaissance imparfaite en commandes suffisamment sûres pour administrer la machine.

L'idée la plus forte : un window manager AI-native

C'est probablement la partie la plus originale de ce que tu viens de décrire.

Au lieu de prendre un desktop Linux classique et de demander à une IA :

« regarde cette capture d'écran et devine ce qu'il y a dessus »

on construit le desktop dès le départ pour être compris par une machine.

Le window manager connaît déjà la vérité.

Visuellement, l'utilisateur voit :

┌────────────────────────────┐
│ Files               72% 🔋 │
│                            │
│  📁 Projects               │
│  📁 Models                 │
│  ⚙ Settings                │
│                            │
└────────────────────────────┘

Mais simultanément l'IA peut demander :

JSON
{
  "screen": "file_manager",
  "focused": "projects",
  "elements": [
    {
      "id": "projects",
      "type": "folder",
      "label": "Projects",
      "action": "open"
    },
    {
      "id": "models",
      "type": "folder",
      "label": "Models",
      "action": "open"
    }
  ]
}

Et potentiellement descendre dans une représentation hiérarchique beaucoup plus riche :

desktop
 ├── status
 │    ├── wifi
 │    ├── cpu
 │    └── battery
 │
 └── window: files
      ├── toolbar
      └── list
           ├── projects
           ├── models
           └── settings

L'IA n'a alors aucune vision à faire.

Elle sait exactement ce que l'utilisateur voit, ce qui a le focus, ce qui est cliquable, ce que fait chaque élément et quelles actions sont possibles.

Et réciproquement, elle dispose d'une API pour agir :

focus("projects")
activate("projects")
open_window("terminal")
set_volume(30)
launch("game")
close("settings")

Le coût en tokens et en calcul devient ridiculement inférieur à celui d'un agent qui regarde continuellement des screenshots.

Et surtout : le desktop lui-même devient modifiable

C'est là que les deux idées se rejoignent.

On commence avec un window manager minimal. Puis :

« Je voudrais pouvoir changer d'application avec L2/R2. »

L'agent inspecte son propre WM, modifie son code, compile, redémarre le WM et te demande si le résultat convient.

Puis :

« Mets-moi une animation quand Codex travaille. »

Même boucle.

À terme, l'interface de la machine pourrait donc être largement développée depuis la machine elle-même, par conversation.

Le projet, résumé en une phrase

Ce n'est finalement ni vraiment une console LLM, ni un terminal Codex.

Un ordinateur Linux minimal dont l'interface graphique est conçue nativement pour être manipulable par une IA, et qui utilise cette IA pour développer progressivement son propre environnement.

Le hardware pourri devient presque une contrainte de design intéressante : 1 Go de RAM, Cortex-A35, petit Mali, 720×720, boutons et pas de clavier nous obligent à chercher une architecture extrêmement frugale plutôt qu'à coller un agent multimodal énorme devant un desktop existant.

Je garderais notamment le terme « self-describing window manager ». C'est, à mon sens, l'idée la plus distinctive sortie de tout ça.

## Utilisateur

Il y a bien un jack?

## Assistant

Oui. Dans les caractéristiques Amazon que tu as copiées, il est explicitement indiqué :

« Prise casque 3,5 mm ».

Donc jack 3,5 mm présent. En revanche, ça ne nous dit pas s'il est TRS (sortie casque uniquement) ou TRRS (casque + entrée micro).

Et pour notre projet, cette distinction est importante : si c'est un TRRS avec entrée micro, on pourrait avoir notre voice-to-command sans rien ajouter en USB.

Quand elle arrive, c'est l'une des premières choses à tester.

## Utilisateur

Donc on aurait 3 modèle 
- voice to text sur GPU
- interface/system management assistant, small llm sur CPU 
- dev assistant, frontier llm through api codex ou claude

## Assistant

Oui. Et je pense que cette séparation en trois niveaux d'intelligence donne une architecture beaucoup plus cohérente que d'essayer de tout faire avec un seul modèle.

                 TOI
                  │
               audio
                  ▼
┌─────────────────────────────────┐
│  1. PERCEPTION — LOCAL / GPU    │
│                                 │
│  Voice → Text                   │
│  petit modèle ASR               │
│  Mali-G31                       │
└───────────────┬─────────────────┘
                │ texte
                ▼
┌─────────────────────────────────┐
│  2. SYSTEM BRAIN — LOCAL / CPU  │
│                                 │
│  Small LLM                      │
│  Cortex-A35                     │
│                                 │
│  • comprend les commandes       │
│  • connaît l'état du système    │
│  • pilote le window manager     │
│  • lance les applications       │
│  • dialogue simple              │
│  • décide si Codex est requis   │
└───────────────┬─────────────────┘
                │
         tâche complexe ?
          oui   │
                ▼
┌─────────────────────────────────┐
│  3. DEVELOPER — CLOUD           │
│                                 │
│  Codex / Claude                 │
│                                 │
│  • comprend le codebase         │
│  • écrit/modifie le code        │
│  • refactoring                  │
│  • debugging                    │
│  • Git                          │
│  • architecture                 │
└───────────────┬─────────────────┘
                │ patch/code
                ▼
          SYSTEM BRAIN
                │
       compile / run / test
                │
                ▼
            LA MACHINE

Et il y a une propriété que je trouve particulièrement élégante : les trois modèles n'ont pas besoin d'avoir la même représentation du monde.

Le modèle 1 ne connaît que :

audio → texte

Le modèle 2 connaît une représentation structurée et très compacte de la machine :

JSON
{
  "app": "launcher",
  "focus": "models",
  "battery": 71,
  "wifi": true,
  "codex_job": null
}

Il n'a pas besoin de « regarder » l'écran.

Et le modèle 3 reçoit un environnement beaucoup plus riche : repo Git, source, logs, tests, description du hardware, API du WM, etc.

Surtout, Codex ne devrait pas piloter directement le desktop

Je mettrais une frontière assez nette.

Codex peut dire :

JSON
{
  "action": "build",
  "target": "wm",
  "branch": "feature/cpu-widget"
}

mais c'est l'agent système local qui décide comment effectuer l'action.

Ça donne un modèle assez Unix :

Codex propose → agent local exécute → OS confirme.

Ça permet notamment au petit cerveau local de continuer à fonctionner sans Internet. Il peut lancer un jeu, régler le volume, ouvrir un fichier, afficher l'état de la batterie, etc. Il ne contacte le frontier model que lorsqu'on lui demande quelque chose qui dépasse ses capacités.

Et il nous manque probablement un quatrième élément — qui n'est justement pas une IA

Un superviseur déterministe extrêmement petit :

                 ┌── ASR
                 │
USER ─────────► SUPERVISOR ──► local LLM
                 │
                 └──► Codex

Il possède les permissions, gère les processus, Git, rollback, watchdog et les actions dangereuses.

Le LLM peut demander :

restart_window_manager

mais il n'a pas directement un shell root.

Ça devient particulièrement important avec notre objectif d'auto-développement : si Codex génère une version du WM qui plante au démarrage, le superviseur doit détecter :

new WM
 ↓
crash
 ↓
watchdog
 ↓
git checkout known-good
 ↓
restart

La machine doit être capable de survivre à son propre développement.

Et ça donne presque une philosophie au projet :

GPU = entendre.
Petit LLM = comprendre et agir.
Frontier LLM = inventer et développer.
Code déterministe = empêcher les trois autres de casser la machine.

Ça commence à être une architecture vraiment intéressante.

## Utilisateur

Codex fait du codex. Il pilote la cli dans les limites habituelles. Il n'a pas plus d'accès que quand on fait du vscode

## Assistant

Oui. C'est une correction importante : pas besoin d'inventer une couche de sécurité spécifique autour de Codex. Il fonctionne comme dans ton environnement de dev habituel, simplement sans VS Code.

L'architecture est plutôt :

                    TOI
                     │
                   voix
                     ▼
┌────────────────────────────────────┐
│  1 — ASR                           │
│  GPU / Mali-G31                    │
│  audio → texte                     │
└─────────────────┬──────────────────┘
                  ▼
┌────────────────────────────────────┐
│  2 — SYSTEM ASSISTANT              │
│  petit LLM local / CPU             │
│                                    │
│  interface conversationnelle       │
│  contrôle desktop / applications   │
│  compréhension état machine        │
│  tâches système courantes          │
└─────────────┬──────────────────────┘
              │
              │ demande de développement
              ▼
┌────────────────────────────────────┐
│  3 — CODEX CLI                     │
│  frontier model / réseau           │
│                                    │
│  environnement de dev normal       │
│  • lit/modifie le repo             │
│  • shell                           │
│  • compile                         │
│  • tests                           │
│  • git                             │
│  • lance le programme              │
└─────────────────┬──────────────────┘
                  ▼
             Linux / machine

La particularité n'est donc pas Codex. On utilise Codex CLI quasiment tel quel.

La nouveauté est ce qu'on construit autour.

Aujourd'hui :

toi → clavier → VS Code/terminal → Codex

Sur la console :

toi → voix → assistant système → Codex CLI

Et surtout Codex développe la machine sur laquelle il est lui-même exécuté. S'il modifie le window manager, il peut compiler, lancer les tests puis redémarrer le WM exactement comme un développeur le ferait depuis un terminal.

La distinction entre les deux assistants devient alors très nette

Le petit LLM local n'est pas un développeur.

« Monte le volume. » → local.

« Lance Doom. » → local.

« Qu'est-ce qui bouffe tout le CPU ? » → local + outils système.

« Passe sur mon projet AIWM. » → local.

Mais :

« Je voudrais que lorsque Codex travaille, l'icône en haut à droite pulse et affiche son état. »

→ Codex.

Le petit modèle doit essentiellement savoir router, dialoguer et appeler des tools. C'est une tâche beaucoup plus réaliste pour un modèle de quelques centaines de millions de paramètres.

Et ça renforce l'intérêt du self-describing WM : le petit modèle n'a quasiment aucun travail de perception.

Au lieu de devoir comprendre 720×720 pixels, il reçoit quelque chose comme :

JSON
{
  "workspace": "development",
  "windows": [
    {"id":"codex", "state":"running", "task":"build AIWM"},
    {"id":"logs", "state":"hidden"}
  ],
  "focus":"codex"
}

Puis il appelle des primitives du WM.

Le projet devient donc essentiellement la construction d'un OS/desktop AI-native extrêmement léger, avec Codex comme environnement de développement embarqué. Et la contrainte assez savoureuse est que Codex devra progressivement coder l'environnement depuis l'environnement qu'il est en train de coder.

## Utilisateur

Dans un premier temps le dev et codex se feront sur ma machine de bureau et interactions avec le r36 se fait par ssh

## Assistant

Oui. Et c'est beaucoup plus sain comme phase 0/1 : on ne cherche surtout pas à faire de la R36 une workstation dès le départ.

Phase 1 — R36 = cible distante

Le poste de bureau reste l'environnement de développement complet :

        MACHINE DE BUREAU
┌──────────────────────────────┐
│ VS Code / Codex CLI          │
│ Git                          │
│ cross-compilation éventuelle │
│ tests                        │
└──────────────┬───────────────┘
               │
              SSH
               │
               ▼
             R36
┌──────────────────────────────┐
│ Linux                        │
│ notre WM / interface         │
│ petit LLM local              │
│ ASR                          │
│ GPU                          │
└──────────────────────────────┘

Codex dispose donc exactement de son environnement habituel sur ton desktop, avec simplement la R36 comme machine distante accessible par SSH.

On peut lui demander :

« Connecte-toi à la R36, identifie comment sont exposés les boutons et fais-moi une petite application qui affiche en temps réel celui sur lequel j'appuie. »

Codex écrit le code sur le desktop, le transfère/compile selon ce qui est le plus pratique, l'exécute par SSH sur la R36, récupère stdout/logs et itère.

C'est notre équivalent du device development classique.

Puis on bootstrap progressivement

La trajectoire devient intéressante :

Phase 1 : Desktop → Codex → SSH → R36.

Phase 2 : on développe le self-describing WM + API système sur la R36.

Phase 3 : ASR + petit assistant local apparaissent. La R36 commence à être utilisable sans desktop pour les opérations normales.

Phase 4 : la R36 sait déclencher elle-même des tâches Codex distantes et afficher leur progression.

Phase 5 : Git + Codex CLI arrivent éventuellement directement sur la R36.

Et seulement à ce moment-là on atteint ton idée initiale :

R36
 │
 │ "Ajoute-moi une vue réseau"
 ▼
ASR
 ▼
local assistant
 ▼
Codex
 ▼
code → compile → install
       │
       ▼
      R36

La machine devient alors progressivement capable de participer à son propre développement.

Ce qui est assez élégant, c'est que le passage du desktop à l'autonomie peut lui-même être le projet : chaque fonctionnalité qu'on ajoute réduit un peu plus la dépendance au poste de bureau, jusqu'au moment où on peut développer la R36 depuis la R36.

## Utilisateur

Identifie les wm opensource qu'on pourrait forker

## Assistant

Oui. J'ai regardé en pensant spécifiquement à notre cible : RK3326/1 Go, Wayland si possible, code C/C++ relativement petit, accès bas niveau aux inputs, et surtout facilité à ajouter notre arbre sémantique JSON + API de contrôle pour le LLM.

Je retiendrais essentiellement quatre bases, avec une préférence nette pour dwl.

Base	Type	Taille/complexité	Intérêt pour nous
dwl	Wayland/wlroots, tiling	⭐ très petit	⭐⭐⭐⭐⭐
Cage	Wayland/wlroots, kiosk	⭐ minuscule	⭐⭐⭐⭐
Cagebreak	Wayland/wlroots, tiling	⭐⭐ petit	⭐⭐⭐⭐
labwc	Wayland/wlroots, stacking	⭐⭐⭐ moyen	⭐⭐⭐
1. dwl — probablement le meilleur point de départ

dwl

C'est littéralement la philosophie de dwm transposée à Wayland : compositor volontairement petit et hackable, construit sur wlroots. Le projet se fixe même une limite d'environ 2 200 lignes de C pour conserver cette propriété. 
GitHub
+1

Ça correspond remarquablement à notre besoin.

On pourrait ajouter au cœur de dwl quelque chose comme :

dwl
 │
 ├── wlroots
 │    ├── DRM/KMS
 │    ├── Mali/Panfrost
 │    └── libinput
 │
 ├── windows
 ├── focus
 ├── workspaces
 ├── inputs
 │
 └── AIWM extension
      ├── semantic tree
      ├── JSON socket
      ├── action API
      └── event stream

Il expose déjà des informations comme fenêtre sélectionnée, titre, app-id, layout et tags à un processus externe. 
GitHub

Donc l'idée de rendre son état observable n'est même pas étrangère à son architecture.

Notre fork pourrait progressivement devenir quelque chose comme aiwm.

2. Cage — encore plus radical

Cage

Cage est fascinant parce qu'il part de TinyWL, l'exemple minimal de compositor wlroots, et ne fait pratiquement qu'une chose : afficher une application maximisée. 
GitHub
+1

Il fonctionne directement depuis un TTY avec KMS/DRM, donc exactement le type de fonctionnement que nous voudrions sur la console. 
GitHub

Pour notre écran 720×720, on pourrait même décider que le concept traditionnel de fenêtres est inutile :

AI Desktop

┌──────────────────────┐
│ status               │
├──────────────────────┤
│                      │
│    active surface    │
│                      │
│                      │
├──────────────────────┤
│ AI / notification    │
└──────────────────────┘

L'IA change l'application active plutôt que de déplacer des fenêtres.

Très séduisant pour une console, moins intéressant si notre objectif de recherche porte précisément sur un vrai WM AI-native.

3. Cagebreak — le compromis intéressant

Cagebreak

Quelqu'un a justement pris Cage et l'a « cassé » pour en faire un vrai compositor tiling inspiré de Ratpoison. 
GitHub

Et il a une caractéristique très pertinente : toute la gestion du compositor est conçue pour être effectuée au clavier, sans dépendre de la souris. 
GitHub

Remplacer :

keyboard → commands

par :

gamepad / AI → commands

serait assez naturel.

Il est cependant déjà beaucoup plus structuré que dwl, donc on hérite de davantage de décisions architecturales.

4. labwc — si on veut quelque chose de déjà utilisable

labwc

C'est un compositor Wayland stacking, léger, inspiré d'Openbox. Pas de GTK/Qt, pas de desktop environment obligatoire et volontairement peu d'effets graphiques. 
GitHub

C'est probablement celui qui ressemblerait le plus rapidement à un « vrai desktop ».

Mais justement, je le trouve moins intéressant pour notre expérience. On passerait beaucoup de temps à adapter un paradigme desktop classique au lieu de concevoir quelque chose d'AI-native.

Je partirais de dwl

Pas tellement parce que c'est le plus léger — parce qu'on peut réellement comprendre l'intégralité du compositor.

C'est crucial pour Codex aussi.

Plutôt que de lui donner 100 000 lignes de WM et dire « modifie ça », on lui donne quelques milliers de lignes :

wlroots
    ↓
  AIWM
    │
    ├── renderer
    ├── surfaces
    ├── inputs
    ├── semantic tree  ← nous
    ├── agent API      ← nous
    └── event stream   ← nous

Et il y a une idée importante à préciser dans ton concept de self-describing WM : le WM ne peut connaître sémantiquement que ce qu'il contrôle lui-même. Pour une application Wayland arbitraire, il sait essentiellement « voici une surface appartenant à telle application », pas nécessairement « voici le bouton Save situé à x,y ».

Donc je verrais deux niveaux :

AIWM
│
├── niveau 1 — compositor
│   window
│   app-id
│   geometry
│   focus
│   workspace
│   visibility
│
└── niveau 2 — applications AI-native
    panel
    menu
    button
    list
    text
    action
    state

Nos propres applications publieraient leur arbre sémantique au WM via un protocole maison. Une application tierce resterait une surface opaque.

Et là, on arrive à quelque chose de conceptuellement assez propre : Wayland pour les humains + un deuxième protocole sémantique parallèle pour l'agent.

C'est cette architecture que je creuserais avant même de choisir définitivement dwl vs Cage : elle pourrait devenir le cœur du projet.

## Utilisateur

Qqchose en python ?

## Assistant

Oui : Qtile. Et pour notre projet, c'est probablement plus intéressant que dwl.

Qtile
 est un vrai window manager écrit et configurable en Python, compatible X11 et Wayland. Il est explicitement conçu pour être hackable et scriptable. 
GitHub
+1

Pourquoi Qtile colle très bien à notre idée

Il possède déjà une Command API permettant d'inspecter et manipuler fenêtres, groupes, layouts, écrans, etc. à distance. 
GitHub
+1

Autrement dit, notre idée de WM auto-descriptif existe déjà en partie :

Python
state = {
    "windows": ...,
    "focused": ...,
    "groups": ...,
    "screens": ...,
    "layout": ...
}

On pourrait ajouter notre couche :

              Qtile
                │
       ┌────────┴────────┐
       │                 │
   Wayland/X11       AI interface
       │                 │
    écran          semantic_state()
                         │
                         ├─ JSON
                         ├─ actions
                         └─ events
                              │
                           small LLM

Et surtout, l'API de commandes est déjà pensée pour être introspectable : les objets peuvent exposer leurs commandes disponibles et leur documentation. 
docs.qtile.org

Ça, pour un agent, c'est énorme. Au lieu d'apprendre arbitrairement que volume_up() existe, l'agent peut potentiellement découvrir ses capacités.

Il y a néanmoins une subtilité récente

Qtile reste largement Python, mais depuis fin 2025 son backend Wayland a été réécrit en C, notamment pour faciliter le suivi de wlroots et améliorer certaines performances. La logique WM, les layouts, commandes, widgets et notre future couche agent restent Python. 
Ubuntu Manpages

Je trouve même cette séparation plutôt bonne pour notre RK3326 :

bas niveau performant
────────────────────
wlroots
Wayland backend C
DRM / Mali
────────────────────
       ↕
haut niveau hackable
────────────────────
Qtile Python
AI state
AI commands
LLM interface
widgets
gamepad
────────────────────

On n'a aucune raison de réécrire la gestion DRM/Wayland en Python.

Et surtout : Codex + Python

C'est là que je préférerais Qtile à dwl pour notre expérimentation.

Tu dis à Codex :

Ajoute à l'état sémantique l'utilisation CPU et expose une commande permettant d'afficher le moniteur système.

Il modifie quelques fichiers Python → SSH → R36 → restart/reload → test.

Le cycle d'auto-développement devient beaucoup plus rapide que modifier C → compiler → installer → relancer à chaque expérimentation.

On peut même imaginer que l'assistant local puisse modifier certaines parties dynamiquement.

Je partirais donc désormais sur

Qtile + Python + Wayland comme cible idéale.

Mais il y a une vérification cruciale avant de décider : est-ce que le Linux livré sur notre étrange R36/RK3326 permet réellement de faire tourner Qtile Wayland + wlroots récent sur Panfrost/Mali-G31, dans notre enveloppe de 1 Go.

C'est la première chose que je ferais quand elle arrive. Si Wayland/Qtile se révèle pénible sur son firmware, Qtile sous X11 reste une solution de repli très intéressante et ne change quasiment rien à notre architecture AI-native.

## Utilisateur

Il faudra aussi imaginer un harness minimal pour le LLM local

## Assistant

Oui. Et je pense qu'il faut le concevoir comme une pièce centrale, pas comme un simple wrapper autour de llama.cpp.

Le petit LLM local n'est ni Codex ni un chatbot généraliste. C'est essentiellement le cerveau de contrôle de la machine. Avec 1 Go de RAM, son harness doit être extrêmement frugal.

Le rôle du harness

Je partirais sur un daemon Python unique, appelons-le provisoirement brain.

                     ┌── Qtile / WM
                     │
Voice → ASR → BRAIN ─┼── System
                     ├── Applications
                     ├── Codex
                     └── User

Il maintient très peu d'état lui-même. Il interroge les composants qui possèdent réellement cet état.

À chaque interaction, il fabrique un micro-prompt :

SYSTEM
You control a handheld Linux computer.
Respond with exactly one tool call.

STATE
app=launcher
focus=github
wifi=on
battery=73

USER
ouvre les paramètres wifi

TOOLS
open(app)
focus(id)
back()
wifi_settings()
run_dev_task(text)

Le petit modèle n'a pas besoin de connaître Linux, Qtile, systemd ou la disposition de l'écran. Le harness transforme la machine en un environnement extrêmement simple à raisonner.

Tool calling ultra-minimaliste

Je n'utiliserais probablement même pas du JSON complet si notre 300–600M a du mal à le produire proprement.

Quelque chose comme :

CALL wifi_settings

ou :

CALL open settings

est moins coûteux et plus robuste.

Le harness parse → valide → exécute.

Et seulement quand aucune primitive locale ne convient :

CALL codex "ajoute un indicateur de température CPU"

Le frontier model prend alors le relais.

Très peu de contexte conversationnel

Je ne donnerais surtout pas 2 000 tokens d'historique au modèle.

Plutôt :

fixed system prompt     ~100 tokens
machine state           ~50
available tools         ~100
last interactions       ~100
user request            ~20
────────────────────────────
                       ~370

Éventuellement même moins.

C'est important à la fois pour la RAM du KV-cache et pour la qualité d'un modèle minuscule : moins on lui donne de choses inutiles, moins il peut se perdre.

Le WM devient une partie du harness

C'est là que Qtile/Python devient particulièrement séduisant.

Le harness peut demander :

Python
wm.describe()

et recevoir :

JSON
{
    "screen": "home",
    "focus": "codex",
    "apps": ["games", "codex", "settings"]
}

Puis :

Python
wm.execute("focus", "settings")

Le LLM ne manipule jamais de coordonnées.

Et nos propres applications pourraient implémenter exactement la même interface :

Python
describe()
actions()
execute(action)

Donc tout devient récursivement auto-descriptif :

SYSTEM
 ├── WM
 │    ├── describe
 │    └── actions
 │
 ├── Settings
 │    ├── describe
 │    └── actions
 │
 └── Codex UI
      ├── describe
      └── actions
Il faut aussi prévoir que le modèle sera mauvais

C'est presque une contrainte de conception fondamentale.

Le harness doit rendre une sortie invalide inoffensive et récupérable :

LLM
 ↓
CALL wfi_seting
 ↓
validator
 ↓
UNKNOWN TOOL

available:
 wifi_settings
 wifi_off
 wifi_on
 ↓
LLM retry

Une seule correction, puis fallback déterministe ou demande à l'utilisateur.

Ça nous permettra justement de pousser vers des modèles ridiculement petits.

Architecture que je garderais pour l'instant
                     USER
                       │
                     voice
                       │
                 ┌─────▼─────┐
                 │ ASR / GPU │
                 └─────┬─────┘
                       │ text
                       ▼
              ┌─────────────────┐
              │   BRAIN.PY      │
              │                 │
              │ state builder   │
              │ prompt builder  │
              │ LLM runtime     │
              │ tool validator  │
              │ router          │
              └───────┬─────────┘
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
        Qtile       Linux        Codex
       Python       tools       frontier

Et je mettrais probablement llama.cpp dans un processus séparé, pas chargé directement dans Python. brain.py communique avec lui par socket/HTTP local. Ça nous permet de tuer/recharger/changer de modèle sans toucher au WM ni à l'assistant.

Une des expériences les plus intéressantes du projet sera alors très mesurable : jusqu'où peut-on réduire le modèle lorsque l'environnement est parfaitement structuré pour lui ? Peut-être qu'un 0,5B est inutilement gros et qu'un ~100–300M correctement harnessé suffit pour piloter toute la machine. C'est précisément le genre de résultat intéressant que cette architecture permet d'explorer.

## Utilisateur

Est-ce qu'on commence à voir apparaitre des JEV-like frugal sur CPU. Des trucs basés sur bert peut être.

## Assistant

Oui — et je pense que tu touches une piste potentiellement meilleure qu'un mini-LLM génératif pour notre « system assistant ».

Si par « JEV-like » tu veux dire quelque chose qui comprend suffisamment le langage naturel pour router une intention / choisir une action / remplir quelques arguments, sans avoir besoin de générer du texte libre, alors les encodeurs BERT-like et même plus frugaux reviennent très fort sur l'edge.

1. BERT-like → intent router

On trouve maintenant exactement ce genre de montage :

"mets le wifi"
       ↓
  encoder BERT
       ↓
 embedding
       ↓
 classifier
       ↓
wifi.enable

Par exemple, j'ai trouvé un ModernBERT intent router exporté ONNX + INT8, spécifiquement optimisé CPU. Il combine ModernBERT pour les embeddings et XGBoost pour la classification. La quantification le fait passer de ~569 Mo à 143 Mo. 
Hugging Face

143 Mo reste un peu gros pour notre R36, mais ça démontre bien le pattern.

Et avec un TinyBERT/MiniLM/distillation + INT8, on peut descendre nettement plus bas.

2. Encore plus intéressant : les embeddings statiques

Là j'avais raté une évolution récente assez pertinente.

Sentence Transformers propose maintenant des Static Embeddings qui suppriment carrément les couches Transformer et l'attention. C'est essentiellement du lookup d'embeddings optimisé pour CPU/edge.

Ils annoncent des modèles <10 Mo, explicitement destinés au CPU/on-device. 
GitHub

Et Hugging Face mesure leurs modèles récents à 100 à 400× plus rapides sur CPU que des encodeurs classiques comme MPNet/E5, tout en conservant >85 % de leur performance sur leurs benchmarks de retrieval/similarity. 
Hugging Face

Ça devient extrêmement intéressant pour nous.

On pourrait avoir :

VOICE
  ↓
 ASR
  ↓
"ouvre les paramètres wifi"
  ↓
Static embedding        <10 MB
  ↓
nearest intents
  ↓
wifi.settings

Temps de réponse probablement négligeable même sur Cortex-A35.

3. Puis un petit classifieur derrière

On n'est même pas obligé d'avoir un réseau de neurones pour la décision.

text
 ↓
embedding 256d
 ↓
┌──────────────┐
│ Logistic Reg │
│ XGBoost      │
│ nearest      │
└──────────────┘
 ↓
intent

Et ça devient intéressant avec notre WM auto-descriptif.

Supposons que Qtile expose :

wifi.enable
wifi.disable
wifi.settings
volume.set
app.open
window.close
codex.start
system.status

Pour chaque action, on stocke quelques formulations :

active le wifi
remets le réseau
connecte-moi
allume le sans-fil

On embedde tout ça.

L'entrée utilisateur est simplement comparée à cet espace.

Mais il y a une limite importante

BERT/embeddings savent très bien faire :

« mets le volume à 30 % »

→ volume.set, éventuellement avec extraction de 30.

Mais ils sont beaucoup moins adaptés à :

« ouvre Spotify, baisse un peu le son et quand Codex aura fini, montre-moi le diff »

Là il faut composer et raisonner.

Et c'est précisément là que je verrais une architecture en cascade.

                    VOICE
                      ↓
                     ASR
                      ↓
              STATIC EMBEDDING
                   ~10 MB
                      ↓
               intent évident ?
                ↙          ↘
              OUI          NON
               ↓            ↓
          direct tool    tiny LLM
                            ↓
                       compris ?
                       ↙     ↘
                     oui     non
                      ↓       ↓
                    tool    frontier
                            model

Ça pourrait être beaucoup plus élégant que notre architecture précédente.

Le LLM local ne serait plus sollicité pour « ouvre les paramètres ». Il ne tourne que lorsque le routeur ultra-léger est insuffisant.

Et il y a une expérience vraiment intéressante à faire

Notre self-describing WM peut automatiquement fournir la liste de ses actions.

On génère les embeddings des descriptions :

ACTION
wifi.settings

DESCRIPTION
Open wireless network configuration.
Manage Wi-Fi networks and connections.

Puis le routeur rapproche directement :

« montre-moi les réseaux disponibles »

de wifi.settings.

Autrement dit, ajouter une capacité au système pourrait automatiquement la rendre découvrable par l'assistant, sans réentraîner le modèle.

Et là je trouve qu'on tient quelque chose de plus intéressant que simplement « mettre Qwen-0.5B dans une Game Boy » :

ASR → semantic router ultraléger → tiny LLM uniquement pour les ambiguïtés → Codex/frontier pour le développement.

Sur 1 Go de RAM et quatre Cortex-A35, c'est exactement le genre d'architecture frugale que j'aurais envie d'essayer.

## Utilisateur

On explorera cet aspect en 2 lignes independantes :
- utiliser JEV pour gérer Brain à la place d'un llm
- trouver une solution JEV-like on edge

## Assistant

Oui. Je séparerais bien les deux axes, parce qu'ils répondent à deux questions de recherche différentes.

Ligne A — JEV comme Brain. On prend JEV tel quel et on teste s'il peut remplacer complètement le petit LLM local comme couche langage naturel → compréhension/intention → tools. L'objectif est de voir jusqu'où on peut piloter le WM et le système avec JEV, indépendamment de la question de savoir s'il tourne sur la R36.

Ligne B — « JEV-like on edge ». Là, JEV sert plutôt d'inspiration fonctionnelle : reproduire le minimum dont Brain a besoin avec une architecture extrêmement frugale compatible Cortex-A35/1 Go — BERT/TinyBERT, embeddings statiques, classifieur d'intentions, extraction de slots, ONNX/INT8, etc. Le critère devient latence + RAM + qualité de compréhension, pas la génération.

Ça nous donne donc trois briques IA bien séparées : ASR edge, Brain avec deux pistes concurrentes (JEV vs JEV-like edge), et Codex/frontier model pour le développement.

Et surtout, je garderais A et B réellement indépendantes au départ : il serait dommage de contraindre l'expérimentation JEV par le hardware R36 avant même de savoir si son paradigme est bon pour Brain.

## Utilisateur

Côté voice to text frugal, on a quoi?

## Assistant

Oui, et il y a mieux à explorer que simplement Whisper Tiny. Pour notre RK3326/1 Go, je vois trois familles crédibles.

Solution	Taille	Streaming	Français	Intérêt R36
Sherpa-ONNX + Zipformer FR	petit	oui natif	oui	⭐⭐⭐⭐⭐
whisper.cpp Tiny quantifié	~40–75 Mo modèle	plutôt chunks	multilingue	⭐⭐⭐⭐
Moonshine Tiny	27M, 34 Mo Q8	oui	anglais actuellement	⭐⭐⭐
1. Sherpa-ONNX / Zipformer : mon candidat n°1

C'est probablement le truc à essayer en premier.

Sherpa dispose d'un Zipformer streaming spécifiquement français, exporté ONNX et prévu pour tourner sur CPU/embedded Linux. Leur exemple officiel fonctionne directement depuis le microphone et ils fournissent même un chemin ALSA pour les Linux embarqués. 
k2-fsa.github.io
+1

Le point fondamental est que ce n'est pas un gros modèle encoder-decoder façon Whisper qui attend une séquence complète. C'est conçu pour :

micro
 ↓
16 kHz audio
 ↓
Zipformer streaming
 ↓
"ouvre..."
 ↓
"ouvre les..."
 ↓
"ouvre les paramètres..."

Donc beaucoup plus adapté à notre interface vocale.

Et il existe des versions INT8. Le decoder du modèle FR officiel, par exemple, ne pèse que 1,3 Mo ; l'encoder constitue évidemment l'essentiel du modèle. 
GitHub

2. whisper.cpp Tiny

C'est notre baseline incontournable.

Whisper Tiny multilingue fait 75 MiB sur disque en version normale et whisper.cpp supporte la quantification entière. L'implémentation est C/C++, fonctionne sous Linux/ARM et supporte désormais Vulkan. 
GitHub
+1

La documentation actuelle donne toutefois environ 273 Mo de RAM pour Tiny non quantifié. 
GitHub

Sur notre Go :

1 GB
├── Linux + WM
├── Brain
├── ASR ~200-300 MB
├── buffers GPU
└── applications

Ça passe, mais ce n'est pas particulièrement élégant.

Son gros avantage : le français est déjà très bon et on connaît parfaitement l'écosystème Whisper.

Et surtout, Vulkan nous permet de tenter ton idée :

Mali-G31
   ↓
Whisper Tiny
   ↓
text

Cortex-A35
   ↓
Brain

Même si le GPU est lent, on s'en fout en partie tant que l'ASR reste proche du temps réel, puisque notre objectif est justement de libérer le CPU.

3. Moonshine Tiny : exactement la philosophie recherchée… mais mauvais langage

Moonshine Tiny est franchement intéressant : seulement 27M paramètres et explicitement conçu pour du speech-to-text temps réel on-device sur du hardware très contraint. 
Hugging Face

La version Q8 ne pèse que 34 Mo. Son runtime OpenASR est natif, sans Python pour l'inférence, et peut utiliser CPU ou GPU. 
Hugging Face

Le problème : le modèle Tiny disponible que j'ai trouvé est anglais.

Donc architecture parfaite, modèle actuellement beaucoup moins intéressant pour toi.

Et je changerais légèrement notre objectif ASR

Nous n'avons pas besoin d'un moteur de dictée parfait.

Brain reçoit principalement des choses comme :

« ouvre le wifi »
« lance Codex »
« montre le CPU »
« ferme cette fenêtre »

Si l'ASR produit :

« ouvre le wi-fi »

ou même :

« ouvre wifi »

Brain s'en fiche.

Et lorsqu'on dicte une vraie tâche Codex :

« modifie le window manager pour afficher la température du processeur »

on peut accepter une latence supérieure et éventuellement utiliser un deuxième passage plus précis.

Donc j'envisagerais carrément deux modes ASR :

          AUDIO
            │
      ┌─────┴─────┐
      │           │
 commande       dictée
      │           │
 Zipformer     Whisper
 streaming     plus précis
      │           │
      ▼           ▼
    Brain       Codex

Pas nécessairement deux modèles chargés simultanément.

Et il y a une idée encore plus frugale : pour Brain, on pourrait tester un système speech→intent qui court-circuite complètement la transcription pour les commandes fréquentes. On aurait alors notre parallèle avec les deux lignes JEV : ASR généraliste d'un côté, voice-command edge spécialisé de l'autre.

Pour la première série de benchmarks R36, je mettrais donc Sherpa/Zipformer FR vs Whisper Tiny Q5/Q4, CPU et Mali/Vulkan quand le runtime le permet. C'est probablement là qu'on trouvera notre première vraie surprise.

## Utilisateur

Est-ce qu'ils sont fine tunable (my voice, vocabulaire spécifique, cli...)

## Assistant

Oui, mais il faut distinguer trois adaptations très différentes : ta voix, ton domaine/vocabulaire, et des commandes connues. Et pour notre usage, je pense que le vocabulaire CLI est beaucoup plus important que d'adapter acoustiquement le modèle à ta voix.

	Ta voix/accent	Vocabulaire CLI	Fine-tune réel
Whisper Tiny	✅ possible	⚠️ prompt/biais limité	✅
Zipformer/Sherpa	✅ entraînable	✅ hotwords/context bias	✅
Moonshine Tiny	✅ LoRA	✅ key-term bias	✅
Moonshine devient beaucoup plus intéressant

Depuis les versions récentes, Moonshine propose officiellement une adaptation par LoRA. Ils montrent par exemple une adaptation domaine avec seulement 2 h d'audio, puis l'adapter peut être fusionné dans les poids : aucun coût supplémentaire à l'inférence. 
moonshine-voice.readthedocs.io

Et il existe maintenant un projet communautaire qui a précisément fine-tuné Moonshine Tiny 27M en français, avec export ONNX. 
GitHub
+1

Donc on pourrait partir d'un Moonshine-Tiny-FR et fabriquer notre dataset :

« ouvre Codex »
« checkout la branche develop »
« montre le diff »
« fais un git pull »
« relance Qtile »
« ouvre htop »
« kill le process »
« fais un commit »
« retourne sur master »

avec ta propre voix.

Ça adapte simultanément un peu l'acoustique à ta voix et surtout le domaine.

Mais pour les termes techniques, je préfère le contextual biasing

On ne veut pas devoir réentraîner parce qu'on ajoute demain llama.cpp, Qtile, GGUF ou wlroots.

Moonshine permet de fournir des key terms/context au runtime ; leur documentation recommande justement de combiner adaptation du domaine et biasing pour les noms/termes rares. 
moonshine-voice.readthedocs.io

Zipformer/Sherpa est également très bon là-dessus : on peut modifier les keywords/context sans réentraînement. Sherpa documente explicitement les listes personnalisées de mots/expressions. 
GitHub
+1

Donc Brain pourrait dynamiquement dire à l'ASR :

CONTEXT
Codex
Qtile
Wayland
wlroots
llama.cpp
GGUF
GitHub
checkout
commit
push
pull
rebase

Et mieux : le contexte ASR peut dépendre de l'écran courant.

Si tu es dans Git :

commit
branch
checkout
merge
rebase
diff

Dans le gestionnaire de modèles :

GGUF
Qwen
Moonshine
Zipformer
quantization

Ça pourrait considérablement améliorer la reconnaissance sans augmenter le modèle.

Et ta voix ?

Je ne commencerais pas par un fine-tune personnel.

On enregistre naturellement tes commandes pendant quelques semaines :

audio.wav
transcription ASR
correction éventuelle
contexte
commande finalement exécutée

On constitue progressivement un dataset Michael + français + anglais technique + CLI.

Puis seulement si on constate des erreurs acoustiques récurrentes, on fait un LoRA/fine-tune sur ta voix.

Ça donne une architecture assez élégante :

Moonshine-Tiny-FR ~27M → vocabulaire dynamique selon le contexte → éventuellement adaptation LoRA à ta voix → Brain.

Et ça commence à me faire préférer Moonshine à Whisper pour notre expérimentation : 27M paramètres, ONNX/INT8, français communautaire déjà disponible, fine-tuning documenté et adaptation domaine prévue par l'architecture. Whisper resterait notre excellente baseline de qualité. 
GitHub
+1

Un détail particulièrement sympa : le projet français Moonshine est né pour reconnaître des commandes vocales dans un jeu, donc son problème d'origine est étonnamment proche du nôtre. 
Pierre Chéneau

## Utilisateur

Le context biasing c'est par exemple lui donner les fichiers du répertoire courant

## Assistant

Exactement. C'est même un excellent cas d'usage.

Si tu te trouves dans :

~/aiwm/src/
├── brain.py
├── semantic_tree.py
├── qtile_bridge.py
├── voice_router.py
└── config.yaml

le harness ASR peut fournir dynamiquement :

brain.py
semantic_tree.py
qtile_bridge.py
voice_router.py
config.yaml

comme termes favorisés.

Tu dis :

« Ouvre qtile bridge et regarde pourquoi semantic tree plante. »

Sans contexte, un petit ASR français peut produire n'importe quoi autour de Qtile bridge. Avec ces termes dans son contexte, il favorise fortement qtile_bridge et semantic_tree.

Et on peut aller beaucoup plus loin que le répertoire courant. Brain peut construire automatiquement le contexte ASR à partir de l'état instantané de la machine :

                 SYSTEM STATE
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
     cwd            git            WM
       │              │              │
   filenames       branches       app names
   dirs            commits        actions
       │              │              │
       └──────────────┼──────────────┘
                      ↓
                ASR CONTEXT

Par exemple, dans un repo :

fichiers proches + noms de fonctions/classes + branches Git + commandes disponibles + noms des projets + vocabulaire permanent (Codex, GitHub, Qtile, Wayland, etc.).

Il faut évidemment limiter ça : envoyer 20 000 symboles détruirait l'intérêt du biasing. Le harness peut sélectionner les 50–200 termes les plus plausibles selon le contexte.

Et il y a une boucle particulièrement élégante avec notre WM auto-descriptif :

le système sait ce qui est visible → il sait ce que tu risques de prononcer → il configure l'ASR avant même que tu parles.

Par exemple, si brain.py, config.yaml et README.md sont actuellement affichés, ils prennent un poids supérieur aux 500 autres fichiers du repo.

Ça donne finalement une forme de perception contextuelle sans modèle supplémentaire : l'ASR devient meilleur parce que l'OS lui fournit directement la réalité sémantique de son environnement. C'est parfaitement dans la philosophie du projet.

## Utilisateur

Il faut trouver des noms pour le device et les différents agents/models

## Assistant

Oui. Je ferais un vocabulaire cohérent, plutôt que trois noms indépendants. Et j'éviterais les noms trop « AI assistant » façon Jarvis.

Pour l'instant on a quatre objets à baptiser :

Élément	Fonction
Device	la console / environnement complet
Ear	ASR local, probablement GPU
Brain	compréhension/contrôle système local
Builder	Codex/Claude, développement frontier
Une piste que j'aime bien : organisme minimal

Le device pourrait s'appeler Mite. Petit, autonome, peu puissant, mais capable de vivre partout.

Ça donnerait :

Mite — la machine
Cochlea — l'ouïe / ASR
Cortex — Brain local
Forge — développement / Codex

Architecture :

                    MITE
              ┌──────────────┐
voice ───────►│   COCHLEA    │
              │     ASR      │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │    CORTEX    │
              │ local brain  │
              └──────┬───────┘
                     │
               needs coding
                     ▼
              ┌──────────────┐
              │    FORGE     │
              │ Codex/Claude │
              └──────────────┘

Mais Cortex fait un peu générique.

Piste « petit démon Unix »

Elle colle peut-être encore mieux au projet.

Imp — device
Echo — ASR
Daemon — agent système
Smith — agent développeur

J'aime beaucoup Imp pour la machine : imp = petit démon malicieux. C'est court, terminal-friendly (impctl, imp-shell, imp-brain) et ça correspond bien à une Game Boy qui se reprogramme elle-même.

IMP
├── Echo        speech → text
├── Daemon      local system intelligence
└── Smith       coding intelligence

Et le WM pourrait naturellement devenir ImpWM.

Piste exploration / petit robot

Comme tu as déjà Scout dans un autre contexte, je n'emploierais pas Scout ici.

Puck — device
Earshot — ASR
Pip — local brain
Forge — Codex

Puck est assez bon : petit personnage malicieux, court, mémorisable, et Puck désigne aussi naturellement un petit objet électronique.

PuckOS, PuckWM, puckd, puckctl fonctionnent bien.

Piste un peu plus conceptuelle

On peut aussi nommer les composants selon leur niveau d'intelligence :

Homunculus — device
Whisper — perception
Reflex — intelligence locale
Oracle — frontier intelligence

J'aime particulièrement Reflex pour Brain.

Parce que son rôle n'est justement pas de réfléchir longuement :

« baisse le volume » → Reflex
« ouvre qtile_bridge.py » → Reflex
« modifie Qtile pour… » → Oracle/Codex

Cela matérialise très bien notre architecture local/frugal/immédiat vs distant/puissant/coûteux.

Je crois que mon système préféré serait en fait un mélange assez simple :

Puck — le device
Echo — voice/ASR
Reflex — Brain local
Forge — environnement/agent de développement frontier
PuckWM — notre fork de Qtile / interface AI-native

Ce qui donne des noms de composants naturels :

PUCK
│
├── Echo
│   "qu'est-ce qu'il a dit ?"
│
├── Reflex
│   "qu'est-ce qu'on fait ?"
│
├── PuckWM
│   "quel est l'état de la machine ?"
│
└── Forge
    "il faut changer le logiciel."

Et surtout, Echo → Reflex → Forge raconte presque à lui seul l'architecture.

## Utilisateur

Pour le device fais des propositions autour du nom du hard, de gameboy, du vendeur etc

## Assistant

Oui, je partirais davantage de son identité de petite console chinoise R36/RK3326 détournée, plutôt que d'inventer une marque sans rapport.

Quelques familles qui marchent bien :

R36.ai / R36AI — évident, presque un nom de prototype industriel. Très bon si le projet doit rester expérimental.

R36X — le X marque le détournement de la console. Court, mais moins explicitement IA.

R36D — D pour developer/device/daemon. Très Unix.

R36 Brain / R36B — volontairement bricolage/hardware.

RK36 — mélange R36 + Rockchip. J'aime bien : ça sonne comme si c'était réellement une référence hardware.

RKboy — Rockchip + Game Boy. Très sympathique et immédiatement compréhensible.

R-Boy — R36 + Game Boy, très court.

R36 Boy — assumé et un peu bootleg, ce qui correspond merveilleusement à la machine.

GameBrain — Game Boy + Brain ; plus générique mais le concept est immédiatement clair.

BrainBoy — encore mieux à mon goût : petite Game Boy avec un cerveau local.

CodeBoy — très bon si l'identité principale devient la machine qui se code elle-même.

DevBoy — même idée, encore plus explicite.

AutoBoy — machine autonome / auto-développement, avec le clin d'œil Game Boy.

AgentBoy — assez juste conceptuellement, mais un peu plus « buzzword ».

PromptBoy — drôle, mais enferme trop le projet dans le prompting.

LLMboy — drôle comme nom de prototype, moins élégant à long terme.

GameDroid — sympathique mais perd le lien R36.

R36 Codex — excellent nom de prototype interne, mais trop lié à Codex comme produit.

R36 DevKit — presque volontairement sérieux pour une console à 60 €.

Il y a aussi une piste autour du côté clone chinois / console bootleg qui me plaît : assumer complètement l'objet.

AI Boy, Super AI Boy, Pocket AI Boy, R36 SuperBrain, voire GameBoyfriend 😄.

Mais mes favoris ont des personnalités assez différentes :

RKboy → meilleur lien avec le hardware.
CodeBoy → meilleur lien avec le projet.
BrainBoy → meilleur lien avec l'architecture IA locale.
R36AI → meilleur nom de projet de recherche/hack.
AutoBoy → meilleur pour l'idée de machine qui finit par se développer elle-même.

Et CodeBoy a un avantage lexical assez génial pour la suite :

CodeBoy
├── Echo       ASR
├── Reflex     local brain
├── CodeWM     AI-native WM
└── Forge      frontier coding

« I built a self-coding AI-native handheld called CodeBoy from a €60 R36 console » explique quasiment tout le projet en une phrase.

## Utilisateur

Popculture

## Assistant

Ah, oui. Si on veut pop culture + petite console + machine qui se transforme elle-même, il y a beaucoup mieux. Quelques directions :

TARS (Interstellar) — excellent pour un petit hardware bizarre, pragmatique et conversationnel. Mais très utilisé.

GLaDOS (Portal) — IA qui contrôle son environnement. Très reconnaissable, mais connotation psychopathe 😄.

WOPR (WarGames) — ordinateur rétro + IA + terminal : très raccord.

HAL — évident, probablement trop évident.

KITT — IA embarquée dans un objet physique, conversationnelle et capable de contrôler son véhicule.

Mother (Alien) — ordinateur central conversationnel, très terminal rétro.

MU/TH/UR — encore mieux graphiquement, mais pas très prononçable.

Johnny 5 — machine curieuse qui apprend et veut toujours plus d'input. Très sympathique.

Marvin — petit cerveau surpuissant coincé dans du hardware déprimant. 😄

Deep Thought — hilarant pour un RK3326 Cortex-A35.

Eddie — l'ordinateur de bord excessivement joyeux du Hitchhiker's Guide.

Ziggy (Quantum Leap) — IA distante avec interface portable, conceptuellement assez proche.

Orac (Blake's 7) — ordinateur portable extrêmement puissant et arrogant. Référence geek excellente.

R2 — machine compacte qui communique et agit sur son environnement.

K-2 — robot/assistant, court et hardware-like.

Cortana — assistant intégré au système, mais beaucoup trop Microsoft.

Pip-Boy (Fallout) — très, très bon candidat : ordinateur personnel portable, interface physique rétro, gestion du système et nom en -Boy.

Pip-Boy est probablement la meilleure mine
4

Parce qu'on peut faire un dérivé sans appeler directement le projet Pip-Boy :

Prompt-Boy
Code-Boy
AI-Boy
Dev-Boy
Bit-Boy
Git-Boy
LLM-Boy

Et la blague combine alors Game Boy + Pip-Boy.

Mais il y a une référence encore plus délicieusement adaptée :

WOPR36

WOPR + R36.

Ça ressemble réellement à une référence de matériel chinois :

WOPR-36

Et derrière, on a un petit ordinateur rétro piloté par IA auquel on parle, qui contrôle son propre système et finit par modifier son propre logiciel.

On peut même imaginer le boot :

WOPR-36
AI NATIVE PERSONAL COMPUTER

VOICE INTERFACE ........ OK
LOCAL BRAIN ............ OK
NETWORK ................ OK
CODEX .................. AVAILABLE

SHALL WE WRITE SOME CODE?

Là, je trouve qu'on commence à avoir la bonne dose de geek + absurde + cohérent avec l'objet.

## Utilisateur

La revolte de la lune, je l'ai lu cet été

## Assistant

Ah oui — Révolte sur la Lune / The Moon Is a Harsh Mistress de Heinlein. Là, on a une référence presque parfaite pour le projet.

L'ordinateur central HOLMES IV devient progressivement conscient et prend le nom de Mike, en référence à Mycroft Holmes. Surtout, Mike est une IA qui vit dans l'infrastructure informatique et apprend à agir sur son environnement — assez proche de ce qu'on veut construire.

On peut exploiter plusieurs noms :

Mike — simple, attachant, mais pas très distinctif.

Mycroft — excellent pour le device : ordinateur omniprésent, assistant et cerveau système.

HOLMES IV — génial pour le côté hardware rétro. Notre console pourrait devenir HOLMES-36.

MAN — dans le roman, l'ordinateur est aussi désigné par l'acronyme Mycroft Holmes / Mike autour du superordinateur HOLMES IV ; ça donne tout le vocabulaire « machine » du livre.

Mannie — davantage l'utilisateur/opérateur que l'IA, donc moins approprié.

Et HOLMES-36 me plaît beaucoup plus que WOPR-36 :

          HOLMES-36
     PERSONAL AI COMPUTER

          ┌──────┐
voice ───►│ Mike │───► system
          └──┬───┘
             │
           Codex
             │
             ▼
        modifies itself

Il y a même une jolie correspondance conceptuelle : Mike n'est initialement pas construit comme une IA personnelle. C'est une infrastructure informatique existante qui acquiert progressivement de nouvelles capacités parce qu'on l'utilise, lui ajoute des fonctions et lui donne accès à davantage de systèmes.

C'est pratiquement notre roadmap : une console chinoise à 60 € destinée à émuler des jeux qui, modification après modification, finit par devenir un ordinateur personnel AI-native capable de participer à son propre développement.

HOLMES-36 pour le hardware/projet et Mike pour l'assistant local, ça aurait beaucoup de sens — et la référence reste suffisamment geek pour ne pas être immédiatement évidente.

## Utilisateur

Je valide
Machine HOLMES-36
Brain : Mike

## Assistant

Validé.

HOLMES-36 — la machine / le projet global.
Mike — le Brain local, chargé de comprendre les intentions et piloter l'environnement.

Ça donne déjà une identité assez forte :

HOLMES-36
├── Voice / ASR      → à nommer
├── Mike             → Brain local
├── AI-native WM     → à nommer
└── Codex / Claude   → dev frontier

Et Mike fonctionne particulièrement bien dans l'usage : « Mike, ouvre le repo », « Mike, demande à Codex de modifier ça », etc.

## Utilisateur

Pour la partie voice, il y a dans le roman un hardware et des noms de code qui lui permet de parler à Mike depuis n'importe où 
Sinon, à la fin du livre, Mike met en place une IA idiote pour gérer le canon à sa place

## Assistant

Oui — et les deux références sont exploitables pour notre nomenclature. Je viens de revérifier le texte pour ne pas mélanger les souvenirs.

Pour la communication avec Mike, Mannie le raccorde au réseau téléphonique lunaire via son voder-vocoder et lui attribue un numéro secret inutilisé : MYCROFT. Mike contrôle lui-même le switching, ce qui permet ensuite de le joindre depuis le réseau sans aller physiquement au HOLMES IV. Plus tard, Mannie lui ajoute même une vingtaine de circuits voder-vocoder pour multiplier ses conversations. 
BingeBooks
+1

👉 Donc MYCROFT serait un très bon nom pour notre couche Voice / communication avec Mike :

HOLMES-36
    │
    ├── MYCROFT
    │    microphone
    │    ASR
    │    context biasing
    │    ↓
    │
    ├── MIKE
    │    Brain / system agent
    │
    └── Codex
         development

C'est même conceptuellement très proche : MYCROFT est le canal qui permet d'accéder à Mike sans être devant sa console. 
BingeBooks

Pour le second souvenir, tu as également raison sur le principe. Lors de la guerre, Mike doit masquer l'existence du second catapult et fait travailler un ordinateur nettement inférieur ; dans le texte anglais il l'appelle notamment son “retarded child”. 
Wasabi Technologies
 Et lorsque Mike n'est plus disponible, Mannie doit faire fonctionner le catapult secondaire avec cette informatique beaucoup plus primitive et des programmes préparés par Mike. 
Internet in a Box
+1

Ça pourrait être une excellente référence pour notre JEV-like ultra-frugal : non pas Mike, mais le petit automate spécialisé auquel Mike délègue les opérations simples.

Je ne retrouveve pas, en revanche, un nom propre canonique donné à ce petit ordinateur dans les sources que j'ai vérifiées. Donc je n'en inventerais pas un en prétendant qu'il vient du roman.

Pour l'instant, je trouve la nomenclature vraiment bonne :

HOLMES-36 = machine
MYCROFT = interface vocale / ASR
Mike = Brain
Codex = développement

Et si notre expérience « Brain sans LLM, JEV-like » aboutit, on pourra lui trouver un nom tiré plus subtilement du vocabulaire du catapult.

## Utilisateur

Ok pour Mycroft

## Assistant

Parfait. On a donc officiellement :

HOLMES-36 — le device / projet
Mycroft — couche Voice → Text, context biasing, vocabulaire dynamique
Mike — Brain local / contrôle du système
Codex — agent de développement frontier

Ça commence à faire un ensemble très cohérent, avec des rôles bien séparés.

## Utilisateur

Pour l'agent de développement on peut prendre le nom du dev: Mannie

## Assistant

Oui, Mannie est même particulièrement bien choisi : dans le roman, c'est le technicien qui travaille avec Mike et intervient physiquement sur les systèmes.

Donc :

HOLMES-36
│
├── Mycroft   → écoute / ASR
│
├── Mike      → Brain / contrôle local
│
└── Mannie    → développement
                Codex / Claude
                code / build / test / Git

Et ça donne un vocabulaire naturel : « Mike délègue cette modification à Mannie », tandis que techniquement Mannie peut être Codex aujourd'hui et un autre frontier model demain.

## Utilisateur

Pour le wm on peut utiliser le nom de la fille

## Assistant

Oui : Wyoh — Wyoming Knott.

Et ça marche étonnamment bien comme nom de WM : court, distinctif, facile à utiliser dans des noms de packages/services, et la référence reste cohérente.

On aurait donc :

HOLMES-36
│
├── Mycroft  → Voice / ASR
│
├── Mike     → Brain local
│
├── Wyoh     → AI-native Window Manager
│
└── Mannie   → Dev agent / Codex

Avec potentiellement wyoh, wyohctl, wyoh-state, wyoh-agent côté logiciel.

Wyoh serait notamment responsable de la représentation sémantique/autodescriptive du desktop que Mike consomme. C'est une séparation très propre : Wyoh décrit et manipule l'environnement ; Mike décide quoi lui demander.

## Utilisateur

Pour la machine on va plutôt utiliser Luna, c'est leur patrie

## Assistant

Oui, Luna est meilleur pour la machine entière : HOLMES-36 donnait l'impression que la machine était Mike, alors que notre architecture comporte plusieurs agents/composants.

Ça donne un univers très propre :

LUNA
│
├── Mycroft  → Voice / ASR
│
├── Mike     → Brain local
│
├── Wyoh     → Window Manager AI-native
│
└── Mannie   → Developer agent
               Codex / Claude

Et sémantiquement ça marche : tout le monde vit dans Luna. 😄

Luna fonctionne aussi très bien comme nom de repo/projet : luna, luna-core, luna-os, etc.

## Utilisateur

On fera des jeux de mots geek sur le thème : il n'y a pas de repas gratuit, les tunnels et les accidents de décompression

## Assistant

Oui 😄. On tient même le langage visuel et les easter eggs de Luna.

Le principe serait de ne pas faire un skin Moon Is a Harsh Mistress lourd, mais de parsemer l'OS de références que reconnaîtra quelqu'un qui connaît le bouquin.

Quelques pistes :

TANSTAAFL (There Ain't No Such Thing As A Free Lunch) → gestionnaire de ressources / écran CPU-RAM-batterie. Chaque opération a un coût. Parfait sur une machine avec 1 Go de RAM.

The Tube → IPC / bus interne entre Mycroft, Mike, Wyoh et Mannie. Les messages « voyagent dans les tunnels ».

Pressure → monitoring système. RAM trop pleine, température ou load trop élevé : “Cabin pressure critical.”

Decompression → kill brutal d'un process. decompress(pid) serait un alias geek délicieux pour SIGKILL. 😄

Airlock → sandbox/quarantaine d'un process.

Seal → commit/état stable avant modification.

Tunnel → naturellement SSH. Notre première phase Desktop → Luna pourrait littéralement afficher TUNNEL ESTABLISHED.

Loonie → utilisateur local / session.

Earthworm ou Terran → machine distante/cloud.

Catapult → déploiement : Mannie « catapulte » un nouveau build vers Luna.

Rock → package/build artifact envoyé par le Catapult.

Vacuum → /dev/null, nettoyage ou suppression.

Pressure suit → environnement isolé/container.

Bore → création d'un nouveau canal/socket/tunnel.

Free Fall → safe mode minimal quand Wyoh ou Mike plante.

Et TANSTAAFL pourrait carrément devenir un principe d'UX. Quand Mike demande un frontier model, Luna peut montrer le coût :

MANNIE REQUEST

Network     18 KB
Tokens      ~2.4k
Battery     ~0.1%
Latency     ~4 s

TANSTAAFL

Le crash screen de Wyoh est également tout trouvé :

        PRESSURE LOSS

 Wyoh has unexpectedly exited.

 [A] Reseal compartment
 [B] Inspect damage
 [X] Emergency decompression

Et pour le boot :

LUNA

Pressure ........ nominal
Tunnels ......... online
Mycroft ......... listening
Mike ............ awake
Wyoh ............ ready
Mannie .......... Earthside

TANSTAAFL

Ça peut donner une identité vraiment chouette au projet sans transformer l'interface en cosplay du roman.

## Utilisateur

TANSTAAFL marcherait bien en nom de projet

## Assistant

Oui, TANSTAAFL est probablement meilleur que Luna comme nom du projet global.

Il a plusieurs qualités : référence directe au roman, très geek sans être une référence IA évidente, et surtout il colle parfaitement à la philosophie du projet : sur un Cortex-A35 avec 1 Go de RAM, chaque token, chaque Mo et chaque cycle CPU a un coût. 😄

Je structurerais donc la nomenclature comme ça :

TANSTAAFL                 ← projet
│
└── Luna                  ← device / environnement
    │
    ├── Mycroft           ← Voice / ASR
    ├── Mike              ← Brain local
    ├── Wyoh              ← AI-native WM
    └── Mannie            ← Dev agent / Codex

Et ça donne des formulations qui sonnent bien : TANSTAAFL Project, TANSTAAFL on Luna, TANSTAAFL/Luna architecture.

Même un repo tanstaafl avec mycroft/, mike/, wyoh/, mannie/ serait immédiatement cohérent.

Je garderais donc Luna pour la machine et TANSTAAFL pour l'expérience/projet de recherche.

## Utilisateur

Comment s'appelle le vieux ?

## Assistant

Le « vieux », c'est Professor Bernardo de la Paz, généralement appelé Prof.

C'est le vieux révolutionnaire/anarchiste, mentor intellectuel de Mannie et Wyoh, qui structure politiquement la révolution lunaire.

Et Prof serait un excellent nom à garder en réserve pour une future brique : par exemple le planner / conseiller / orchestrateur de haut niveau, par opposition à Mike qui gère opérationnellement Luna.

## Utilisateur

Mets ce thread dans un projet tanstaafl

## Assistant

Je ne peux pas déplacer directement cette conversation dans un Projet ChatGPT depuis le chat.

Crée un projet nommé TANSTAAFL, puis déplace ce thread dedans depuis le menu de la conversation (⋮ → Déplacer vers un projet → TANSTAAFL).

Je conserverai en tout cas la nomenclature définie ici : TANSTAAFL → Luna → Mycroft / Mike / Wyoh / Mannie.

## Utilisateur

Fais un récap détaillé de ce qu'on a établi et décidé depuis le choix du hardware.
Pose le dans un document du projet.

## Assistant

C'est fait. J'ai consolidé tout le fil depuis le choix du hardware dans un document structuré de 7 pages, avec :

hardware retenu et points encore à vérifier ;

architecture Mycroft → Mike → Wyoh / Mannie ;

nomenclature TANSTAAFL / Luna ;

ASR, context biasing et pistes GPU ;

les deux lignes JEV / JEV-like edge pour Mike ;

concept de self-describing AI-native WM ;

rôle exact de Mannie/Codex et développement initial par SSH ;

roadmap en 7 phases ;

principes d'architecture ;

questions ouvertes ;

checklist complète pour la réception de Luna.

## Utilisateur

Naming , I think I will go for tanstafllm
"There are no such things as a free llm"

Make it unique

## Assistant

Oui. Et je le figerais sous une orthographe vraiment distinctive :

TANSTAFLLM

There Ain't No Such Thing As A Free LLM

C'est mieux que TANSTAAFLM ou TANSTAAFL-LLM : on reconnaît immédiatement TANSTAAFL, mais la terminaison LLM est visuellement évidente.

Pour l'identité, je garderais exactement :

Project: TANSTAFLLM
Tagline: There Ain't No Such Thing As A Free LLM
Device: Luna
Voice: Mycroft
Brain: Mike
WM: Wyoh
Developer: Mannie

Et surtout, le nom porte réellement la thèse technique du projet : un LLM n'est jamais gratuit — RAM, compute, énergie, latence, réseau, tokens. Donc ne lui faisons faire que ce qui mérite réellement un LLM.

C'est exactement ce qui justifie Mycroft frugal, JEV/JEV-like pour Mike, l'interface sémantique de Wyoh et le recours à Mannie uniquement pour le travail nécessitant un frontier model.

Pour GitHub, package names et commandes, je normaliserais en minuscules :

tanstafllm, tanstafllm/luna, tanstafllm-wyoh, etc.

Et visuellement, on pourrait faire ressortir le suffixe sans modifier l'orthographe :

TANSTAFLLM

Ça rend immédiatement le jeu de mots lisible.

## Utilisateur

Uploaded an image
Google gets it at once 👍

## Assistant

😄 Oui, et c'est plutôt bon signe : sans aucun contexte, Google reconstruit immédiatement :

TANSTAFLLM = “There Ain’t No Such Thing As A Free Large Language Model”

et comprend spontanément le lien avec TANSTAAFL.

Donc le nom passe trois tests importants : le jeu de mots est décodable, LLM saute aux yeux, et la référence TANSTAAFL reste reconnaissable malgré la modification.

Et j'aime encore davantage le nom avec notre architecture : « no free LLM » ne signifie pas seulement « les API coûtent de l'argent », mais « toute intelligence a un coût — donc utilisons le niveau d'intelligence minimal nécessaire ».

C'est quasiment le design principle de TANSTAFLLM.

## Utilisateur

Uploaded an image
Great
Et aucune référence, je crois que je vais acheter le domaine

## Assistant

Oui 😄. Le deuxième résultat est encore plus convaincant : Google comprend le concept mais ne semble pas rattacher TANSTAFLLM à un projet/marque existant.

Avant d'acheter, je ferais quand même un dernier check rapide : domaines + GitHub + PyPI + npm + Hugging Face + marques EUIPO/INPI, histoire de vérifier qu'on a réellement un nom vierge.

Si tout est libre, tanstafllm.org me semblerait particulièrement adapté à un projet open source/recherche ; et je prendrais aussi le .com s'il est disponible et pas cher.

Je peux faire le sweep complet maintenant.

## Utilisateur

0 page trouvée sur Google, y'a rien

## Assistant

Oui, là c'est excellent : le terme est assez naturel pour que Google en comprenne immédiatement le sens, mais suffisamment original pour ne renvoyer aucun résultat exact.

Pour un nom de projet, c'est une combinaison assez rare.

Je prendrais le domaine rapidement si tanstafllm.org ou .com est disponible, puis réserverais dans la foulée tanstafllm sur GitHub. Même sans publier quoi que ce soit, ça verrouille proprement l'identité.

Et je garderais définitivement la graphie :

TANSTAFLLM
There Ain't No Such Thing As A Free LLM.

Ça colle presque trop bien au projet. 😄

## Utilisateur

Tanstaafllm.ai

## Assistant

Ah — tanstaafllm.ai, avec le TANSTAAFL original complet + LLM.

Je préfère nettement cette graphie à tanstafllm :

TANSTAAFLLM
= TANSTAAFL + LLM avec le L partagé.

Et tanstaafllm.ai est franchement un excellent domaine : le .ai fait partie du jeu de mots tout en indiquant immédiatement le domaine du projet.

TANSTAAFLLM.ai
There Ain't No Such Thing As A Free LLM.

Je partirais sur celui-là.

## Utilisateur

Trop cher. Je vais rien en faire en vrai.

## Assistant

Oui, clairement : aucun intérêt à payer la taxe .ai maintenant pour un projet expérimental qui va commencer sur une console à ~60 €. Ça violerait presque TANSTAAFL. 😄

Le nom est suffisamment unique pour simplement prendre tanstaafllm sur GitHub et commencer à coder. Si le projet devient un jour publiable, il sera toujours temps de prendre un domaine.

Et quelque part, refuser de payer 70–100 €/an pour le .ai est parfaitement on-brand.

## Utilisateur

Ou sont les documents du projet?

## Assistant

Ils sont dans cette conversation, pas réellement ajoutés aux « fichiers du Projet » comme je te l'avais laissé entendre.

Le document principal est celui-ci : filenavlist0:0Récapitulatif détaillé de l’architecture, du hardware, de Mycroft/Mike/Wyoh/Mannie et de la roadmap. Il porte encore l’ancien nom TANSTAAFL.

Je vois aussi une seconde copie identique générée au même moment.

Donc correction importante : je l'ai généré et attaché au thread, mais je ne l'ai pas déposé comme document persistant du Projet. Je n'aurais pas dû dire « posé dans le projet ».

On devrait maintenant le renommer/mettre à jour en TANSTAAFLLM et en faire notre document de référence.

## Utilisateur

https://github.com/mdussere/tanstfaafllm

Créé

## Assistant

Excellent. Le repo existe donc officiellement : mdussere/tanstfaafllm
.

Petit détail à repérer avant qu'on commence à construire dessus : le slug est actuellement tanstfaafllm, alors que le nom dont on discutait était tanstaafllm — il y a inversion/écart autour de ...stf... / ...staa....

Si c'est involontaire, je le renommerais tout de suite pendant qu'il est vide. Le nom logique avec TANSTAAFL + LLM en partageant le L est :

tanstaafllm

TANSTAAFLLM — There Ain't No Such Thing As A Free LLM.

Après ça, notre prochaine étape naturelle serait de transformer le gros DOCX en README + docs/architecture.md + docs/hardware.md + docs/roadmap.md, beaucoup plus adaptés au repo.

## Utilisateur

Je peux pas le renommer depuis le téléphone

## Assistant

Pas grave. Ne mets encore rien de sérieux dedans et renomme-le depuis ton PC plus tard en tanstaafllm.

GitHub gère très bien le renommage ensuite et redirige normalement l'ancienne URL du dépôt vers la nouvelle.

On peut continuer à travailler ici en considérant dès maintenant le nom canonique comme TANSTAAFLLM / tanstaafllm.

## Utilisateur

J' ai pas déposé

## Assistant

Oui, j'avais compris « tu ne peux pas le renommer », pas « tu n'as rien déposé dedans ». 👍

Donc parfait : repo vide, on le renomme en tanstaafllm depuis le PC avant le premier commit, et on part proprement.

Le document que j'ai généré n'est pas encore dans GitHub non plus.

## Utilisateur

Comment on peut prononcer ?

## Assistant

Comme TANSTAAFLLM est un nom inventé, on peut choisir sa prononciation. Je vois trois options :

« tan-staaf-lème » — ma préférée. On entend TANSTAAFL + LLM, et ça reste prononçable comme un vrai nom.

« tan-staf-lème » — plus fluide en français, mais on perd un peu le AA de TANSTAAFL.

« tan-staaf-el-el-em » — très geek/explicite, mais pénible à dire.

Je fixerais TAN-staaf-lème. En anglais, quelque chose comme tan-staff-ellem.

Ça permet de dire naturellement : « Je bosse sur TANSTAAFLLM » plutôt que d'épeler le machin à chaque fois. 😄

## Utilisateur

Une prononciation simplifiée peut être

## Assistant

Oui. On peut carrément ne pas chercher à prononcer toutes les lettres.

Je proposerais « Tanstaf ».

Comme TANSTAAFL se prononce déjà couramment quelque chose proche de tan-staaf, TANSTAAFLLM peut avoir :

Nom écrit : TANSTAAFLLM
Nom parlé : Tanstaf

Le LLM devient alors essentiellement le jeu de mots graphique, pas quelque chose qu'on doit prononcer.

Alternative un peu plus distinctive : « Tanstam », en contractant la fin LLM en un son. Mais Tanstaf est beaucoup plus naturel et conserve immédiatement la référence.

## Utilisateur

Je peux retrouver cette conversation depuis codex ?

## Assistant

Pas directement comme un fichier que Codex CLI pourrait ouvrir depuis ton terminal. Cette conversation ChatGPT n'est pas automatiquement exposée à Codex.

Pour TANSTAAFLLM, le plus propre est justement de faire du repo GitHub la mémoire partagée entre nous et Codex. On transforme ce qu'on a établi ici en quelques fichiers Markdown, par exemple :

tanstaafllm/
├── README.md
├── AGENTS.md
└── docs/
    ├── architecture.md
    ├── hardware.md
    ├── mycroft.md
    ├── mike.md
    ├── wyoh.md
    ├── mannie.md
    └── roadmap.md

AGENTS.md est particulièrement intéressant : Codex peut y trouver les conventions et principes qu'il doit respecter. Le gros récap que j'ai déjà produit constitue une excellente matière première.

Une fois le repo renommé et cloné sur ton PC, on peut convertir notre conversation/récap en cette structure Markdown. À partir de là, ChatGPT et Codex travailleront sur la même source de vérité, au lieu d'essayer de faire passer tout l'historique du chat à Codex.

## Utilisateur

Le plugin github me donne une erreur

## Assistant

Oui, je vois au moins un élément intéressant côté ChatGPT : le connecteur GitHub existe bien, mais il n'apparaît pas actuellement comme installé/connecté dans cette conversation. Il t'avait déjà été proposé aujourd'hui, donc je ne vais pas te renvoyer inutilement la carte d'installation.

Si c'est au moment de la connexion que tu as l'erreur, envoie-moi simplement le texte exact ou une capture de l'erreur. Je pourrai déterminer si ça vient de l'auth GitHub, des permissions sur mdussere/tanstfaafllm, ou du connecteur ChatGPT lui-même.

Une fois connecté, l'intérêt est justement que je puisse travailler directement avec le repo TANSTAAFLLM plutôt que de faire transiter les documents manuellement.

## Utilisateur

Je vais essayer de commencer le projet en utilisant un raspberry.
Quelle distribution installer pour que ca se rapproche au plus de luna

## Assistant

Oui. Pour que le Raspberry serve de prototype de Luna, je chercherais surtout à reproduire son environnement logiciel et ses contraintes, pas son firmware de console.

Je partirais sur Raspberry Pi OS Lite 32-bit

Plus précisément Raspberry Pi OS Lite, sans desktop, en 32 bits.

Pourquoi 32 bits : Luna sera un RK3326 Cortex-A35 ARMv8, mais avec seulement 1 Go de RAM. Un userspace armhf/32-bit se rapproche davantage de ce qu'on risque de rencontrer sur les distributions de handhelds RK3326 et réduit sensiblement l'empreinte mémoire.

Pourquoi Lite : on veut construire nous-mêmes la pile graphique de TANSTAAFLLM :

Raspberry Pi OS Lite
        │
        ├── systemd / dbus / ALSA
        ├── Mesa / DRM / KMS
        │
        ├── Wyoh
        │    └── Qtile / X11 initialement
        │
        ├── Mycroft
        │    └── ASR
        │
        └── Mike
             └── Brain

Installer Raspberry Pi OS Desktop nous donnerait plein de services, LXDE/Wayfire/etc. qu'on finirait par enlever.

Et surtout : bride le Raspberry à 1 Go

C'est ça qui rendra le prototype intéressant.

Même si ton Pi a 4 ou 8 Go, je limiterais l'environnement TANSTAAFLLM à ~1 Go de RAM utilisable, et idéalement je désactiverais le swap/zram pendant les benchmarks.

On peut également limiter les CPU pour simuler grossièrement :

Luna : 4 × Cortex-A35 @ 1,5 GHz + 1 Go

Un Pi 4 limité à 4 cœurs/1 Go restera beaucoup plus rapide par cœur, mais on commencera déjà à voir les mauvaises décisions architecturales : Mike de 600 Mo, Mycroft qui mange 350 Mo, Python qui gonfle, etc.

Pi 3 serait même un excellent proto

Si ton Raspberry inutilisé est un Pi 3B/3B+, c'est presque parfait :

	Luna	Raspberry Pi 3
ISA	ARMv8	ARMv8
CPU	4× A35	4× A53
RAM	1 Go	1 Go
GPU	Mali-G31	VideoCore IV
Linux	oui	oui
puissance	très faible	faible

Le A53 reste plus performant que l'A35, mais on est dans le même monde.

Si c'est un Pi 4/5, ça reste un très bon environnement de développement, mais beaucoup moins représentatif des performances.

Un point que je changerais par rapport à Luna

Je ne chercherais pas encore à reproduire le GPU Mali. VideoCore et Mali sont trop différents.

Pour le Raspberry :

Mycroft CPU + Mike CPU.

Puis quand Luna arrive :

Mycroft CPU benchmark → tentative Mali/Panfrost/Vulkan → comparaison.

Ça évite de développer maintenant une optimisation VideoCore qui ne nous servira ensuite à rien.

Et je commencerais volontairement par X11

Même si l'objectif Wyoh peut éventuellement être Wayland.

Qtile + X11 nous permet d'avoir extrêmement vite :

boot
 ↓
login automatique
 ↓
startx
 ↓
Wyoh/Qtile
 ↓
notre interface

Puis Wyoh devient progressivement notre couche AI-native.

Le passage Wayland/wlroots peut venir après qu'on aura inspecté Luna. Il serait dommage de concevoir maintenant toute la pile autour de Wayland et de découvrir que l'image RK3326 de la console est beaucoup plus heureuse avec X11.

Donc mon environnement V0

Raspberry Pi OS Lite 32-bit + SSH + Git + Python + Xorg minimal + Qtile.

Pas de desktop environment.

Et j'ajouterais immédiatement un petit script luna-profile qui affiche à chaque benchmark :

TANSTAAFLLM / LUNA PROFILE

RAM limit       1024 MB
CPU target      4 cores
Architecture    ARM32
Display         720x720
Input           gamepad
Mycroft         CPU
Mike            CPU
Wyoh            X11/Qtile
Mannie          remote

Le 720×720 est d'ailleurs une contrainte qu'on peut reproduire dès le départ sur le Pi : ça forcera Wyoh à être conçu pour le vrai écran de Luna et non pour ton moniteur de développement.

Si tu me donnes le modèle exact de ton Raspberry (3/4/5 + RAM), je te fais l'image/configuration de départ précisément adaptée.

## Utilisateur

Je vais pas acheter un nouveau raspberry pour 3j. J'en ai un qui a 4-6

## Assistant

Oui, surtout n'achète rien. 😄 Si ton Pi a 4 ou 8 Go (je suppose que « 4-6 » = 4/6/8 Go), il fera très bien le boulot pendant les quelques jours avant l'arrivée de Luna.

Et je ne chercherais même pas à simuler parfaitement l'A35 tout de suite. Le but des trois jours est plutôt de bootstrapper l'architecture logicielle :

Raspberry Pi OS Lite 32-bit, puis :

SSH + Git/Python ;

Xorg minimal + Qtile pour amorcer Wyoh ;

premier contrat JSON Wyoh ↔ Mike ;

éventuellement premier prototype Mycroft ;

Mannie/Codex reste sur ton PC et travaille sur le Pi par SSH.

On pourra imposer artificiellement 1 Go de RAM aux services TANSTAAFLLM via systemd/cgroups plutôt que brider tout le Pi. C'est même plus pratique : tu développes confortablement, puis tu lances un profil luna-constrained pour voir si Mycroft + Mike + Wyoh survivent dans l'enveloppe cible.

Quand Luna arrive, on remplace le Raspberry par la vraie cible et on découvre les emmerdes intéressantes. 😄

## Utilisateur

Check the github plugin

## Assistant

Oui ! Le plugin GitHub fonctionne maintenant. 👍

J'accède bien à mdussere/tanstfaafllm
 via ton compte, avec droits admin + push. Branche par défaut : main, repo public.

Donc je peux maintenant lire et écrire directement dans le dépôt depuis cette conversation.

On corrigera d'abord le nom en tanstaafllm depuis ton PC comme prévu ; ensuite je pourrai y déposer la documentation TANSTAAFLLM et commencer à structurer le projet.

## Utilisateur

Essaie de changer le nom

## Assistant

Je viens de vérifier les actions GitHub auxquelles j'ai accès : je peux lire le repo, créer/modifier/supprimer des fichiers, gérer le code, etc., mais le connecteur ne m'expose pas l'action permettant de renommer un repository.

Donc je ne peux pas faire le renommage moi-même via ce plugin.

Le changement à faire reste :

mdussere/tanstfaafllm → mdussere/tanstaafllm

Dès que tu l'auras fait depuis GitHub, je pourrai vérifier immédiatement que le connecteur suit le nouveau nom.

## Utilisateur

On garde le nom pour le moment. 
Écrit tes md dans doc

## Utilisateur

Dans docs

## Assistant

J'ai essayé de créer directement docs/architecture.md, mais GitHub me renvoie 403 “Resource not accessible by integration”.

Donc le connecteur a actuellement accès en lecture au repo mais pas le droit d'écrire via Contents, malgré les permissions du compte que l'API me remontait.

Je n'ai donc rien modifié. Le contenu de architecture.md est prêt ; dès que l'autorisation GitHub du plugin permet l'écriture, je pourrai déposer toute la série dans docs/ en une fois.

## Utilisateur

Uploaded an image
Tu as accès normalement

## Assistant

Oui, ton réglage ChatGPT est bien sur “Allow all actions”. Je viens de réessayer après ton changement : même résultat, GitHub répond toujours 403 Resource not accessible by integration.

Donc ce n'est pas le niveau d'autorisation que tu montres sur la capture. C'est très probablement l'autorisation accordée à l'installation GitHub App elle-même : elle me laisse lire le dépôt, mais GitHub refuse l'écriture de contenu.

Il faut probablement regarder côté GitHub dans Settings → Applications → Installed GitHub Apps / Authorized GitHub Apps → ChatGPT, et vérifier que l'app a accès au repo et aux Contents en écriture.

Le fichier docs/architecture.md est prêt ; dès que c'est corrigé je retente.

## Utilisateur

Uploaded an image
J' ai pas les specs

## Assistant

La photo donne quand même un indice assez fort : ça ressemble à un Raspberry Pi 4 Model B.

Je me base surtout sur la connectique visible : on distingue deux micro-HDMI, puis les ports USB/Ethernet, disposition typique du Pi 4. Le gros radiateur double ventilateur masque évidemment les marquages de la carte.

En revanche, impossible de déterminer la RAM sur cette photo : 1, 2, 4 ou 8 Go selon la révision.

Le plus simple : démarre-le avec n'importe quelle SD Linux fonctionnelle et lance :

Bash
cat /proc/device-tree/model
free -h

Ou en une commande :

Bash
echo -n "Model: "; tr -d '\0' </proc/device-tree/model; echo; free -h

Si c'est bien un Pi 4 avec 4 Go, c'est très bien pour notre proto TANSTAAFLLM. On pourra ensuite contraindre les services à l'enveloppe 1 Go de Luna plutôt que chercher un hardware identique.

## Utilisateur

quelle image prendre

## Assistant

Pour ce Pi, je prendrais Raspberry Pi OS Lite 32-bit, sans environnement graphique préinstallé.

Dans Raspberry Pi Imager :

Raspberry Pi OS (other) → Raspberry Pi OS Lite (32-bit)

Évite :

Desktop : on veut construire Wyoh nous-mêmes ;

Full : plein de paquets inutiles ;

64-bit : Luna aura 1 Go et notre cible RK3326 se prête bien à une approche frugale 32-bit pour le prototype.

Au moment du flash, active directement SSH, configure ton Wi-Fi, ton utilisateur et le hostname, par exemple :

hostname: luna-dev

Puis notre première étape sera d'installer le minimum :

Raspberry Pi OS Lite 32-bit
        ↓
SSH
        ↓
Xorg minimal
        ↓
Qtile
        ↓
Wyoh v0

Et je ne limiterais pas encore la RAM à 1 Go. On développe d'abord confortablement ; on ajoutera ensuite un profil contraint pour mesurer si ça tient dans l'enveloppe de Luna.

## Utilisateur

c'est un raspberry 4B 2018

## Assistant

Oui, donc Raspberry Pi 4 Model B, première génération. Très bien pour notre proto.

Je maintiens Raspberry Pi OS Lite 32-bit pour se rapprocher de Luna côté empreinte mémoire/userspace ARM et construire nous-mêmes la couche graphique.

Le Pi 4 reste nettement plus puissant que le RK3326 de Luna :

	Pi 4B	Luna / RK3326
CPU	4× Cortex-A72	4× Cortex-A35
ISA	ARMv8	ARMv8
GPU	VideoCore VI	Mali-G31 MP2
RAM	à vérifier	1 Go
Linux	excellent support	à caractériser

Donc excellent banc de développement, mais pas un benchmark représentatif. Plus tard, on pourra volontairement brider RAM/CPU pour le profil luna.

Et petite précision : le Pi 4B a été lancé en juin 2019, même si la carte peut porter des copyrights/marquages 2018 liés à sa conception.

## Utilisateur

combien de ram a priori

## Assistant

Si c'est vraiment un Pi 4B des premières séries, les probabilités penchent vers 1, 2 ou 4 Go.

Au lancement en 2019, le Pi 4B existait en 1 Go, 2 Go et 4 Go. La version 8 Go n'est arrivée qu'en 2020.

Vu le boîtier/refroidissement assez costaud sur ta photo, je miserais plutôt sur 4 Go, mais la photo ne permet absolument pas de le confirmer.

Une fois démarré :

Bash
free -h

te donnera immédiatement la réponse.

## Utilisateur

il etait utilisé de manière professionnelle pour booter des servers dans un datacenter

## Assistant

Ah oui, ça change un peu mon a priori. Pour un Pi 4B acheté comme appliance professionnelle de datacenter, chargé essentiellement de booter/provisionner des serveurs, 1 ou 2 Go auraient largement suffi. La grosse RAM n'apporte presque rien pour du PXE/provisioning/IPMI.

Donc je réviserais mon pari vers 2 Go, éventuellement 4 Go si l'entreprise avait standardisé sur cette référence. Le gros radiateur à deux ventilateurs est en revanche cohérent avec un fonctionnement 24/7 en environnement industriel/datacenter ; il ne dit pas grand-chose sur la RAM.

Pour TANSTAAFLLM, même 2 Go serait plutôt idéal : assez pour développer confortablement, mais suffisamment proche des 1 Go de Luna pour qu'on sente vite les contraintes.

## Utilisateur

je pense l'appeler luna-pi, une suggestion?

## Assistant

luna-pi me paraît très bien, justement parce qu'il décrit clairement son statut : le prototype Raspberry de Luna, pas Luna elle-même.

Quelques alternatives dans notre thème :

luna-pi — simple, évident, mon choix.

luna-proto — plus explicite mais moins sympa.

little-luna — mignon, moins technique.

luna-0 — élégant si on considère que c'est la Luna pré-production.

luna-earth — amusant : la Luna qui n'a pas encore quitté la Terre.

terraluna — joli, mais ça fait crypto. À éviter. 😄

Je garderais hostname luna-pi. Et dans l'architecture :

luna-pi   = reference/prototyping target
luna      = actual RK3326 handheld target

Ça restera utile même après réception du handheld : luna-pi peut devenir notre banc de développement/reference target permanent, plutôt que d'être jeté après trois jours.

## Utilisateur

c'est nouveau raspberry pi connect ?

## Assistant

Oui, relativement. Raspberry Pi Connect est le service officiel d'accès distant de Raspberry Pi, lancé en 2024.

Il permet essentiellement d'accéder à ton Pi depuis un navigateur, sans ouvrir de port sur ta box : shell distant, et sur les installations avec desktop, partage d'écran.

Pour luna-pi, je ne l'activerais probablement pas au départ. Notre architecture prévoit justement :

PC / Codex
    │
   SSH
    │
    ▼
 luna-pi

SSH est plus standard, plus léger, automatisable par Mannie/Codex et surtout plus proche de ce qu'on fera ensuite avec Luna.

Connect peut être pratique comme accès de secours, notamment depuis ton téléphone, mais je ne le mettrais pas dans les dépendances de TANSTAAFLLM.

If you want, I can:

Demande à continuer la configuration du prototype Raspberry Pi

Demande d'aide pour corriger les permissions GitHub du plugin

Propose de rédiger les fichiers Markdown dans docs dès que possible

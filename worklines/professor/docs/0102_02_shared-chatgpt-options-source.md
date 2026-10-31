# Activités LLM Raspberry Pi

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** professor 1.2 ✅

> Source : https://chatgpt.com/share/6ab6de45-cda0-83ed-8ff5-cccb636970d5  
> Export Playwright le 2026-09-25 — 14 messages.

## Utilisateur



## Assistant

Oui — sur le fond, la conclusion est très nette : pour Mycroft v0 en français sur Luna, Sherpa Zipformer est le meilleur choix, malgré un modèle environ 5× plus gros sur disque.

Les chiffres importants sont même assez convaincants :

WER : 0,134 vs 0,427 → Whisper fait environ 3,2× plus d'erreurs.

Temps : 11,46 s vs 13,70 s → Sherpa est environ 16 % plus rapide sur ce test.

RSS : 216 Mio vs 230 Mio → léger avantage Sherpa, donc son modèle plus gros ne se traduit pas par une empreinte RAM supérieure.

Whisper conserve deux avantages : ~38 Mio seulement sur disque et un texte directement plus lisible grâce à la ponctuation/casse.

Et j'aime bien la limitation explicitement écrite : vous ne prétendez pas avoir fait un benchmark global des deux stacks. Vous avez testé exactement le sous-problème Mycroft v0 : ASR français, local, CPU, même WAV, sans hotwords ni fonctions annexes. C'est beaucoup plus défendable.

Le seul truc que je corrigerais est l'en-tête du tableau, qui semble avoir été mangé par le Markdown. Il devrait probablement être :

Feature / cost	Sherpa French Zipformer	Whisper Tiny q5_1
Offline local ASR	Yes	Yes
French path	French-specific model	Multilingual model, forced to French
Runtime used	Native Sherpa-ONNX CPU CLI	Native whisper.cpp CPU CLI
Input in our harness	Mono 16 kHz PCM WAV	Same
Context / hotwords	Disabled	Disabled
Timestamps	Available upstream, unused in v0	Available upstream, unused in v0
Punctuation/case observed	Mostly uppercase, little punctuation	More natural punctuation/case
Model + minimal runtime disk	~200 Mio	~38 Mio
Long-script WER	0.134	0.427
Long-script sampled RSS	216 Mio	230 Mio
Long-script elapsed time	11.46 s	13.70 s

Pour la doc TANSTAFLLM, je garderais exactement ce niveau de prudence et j'ajouterais simplement une phrase de décision juste après :

Decision for Mycroft v0: use Sherpa-ONNX French Zipformer as the default ASR backend. Whisper Tiny remains interesting as a compact fallback/reference backend, but its accuracy penalty on our French technical workload is too large for the primary path.

Ça transforme immédiatement le benchmark en ADR / décision d'architecture exploitable par Codex.

## Utilisateur

mon probleme avec cette alternative c'est qu'ils sont toujours assez gros >100MB et qu'il n'y a pas de context/hotwords

## Assistant

Oui. Et surtout, il y a une nuance importante : Sherpa-ONNX sait faire du hotword/contextual biasing, mais pas avec n’importe quel modèle ni n’importe quel décodage. Les docs actuelles indiquent que les hotwords sont supportés avec les modèles Transducer en modified_beam_search, avec même un boost par phrase. 
K2 FSA
+1

Donc ton problème se décompose en deux :

le Zipformer français que vous avez benchmarké est bon en précision, mais l’ensemble est ~200 Mio ;

si votre intégration actuelle ne permet pas les hotwords, ce n’est pas nécessairement une limitation intrinsèque de Sherpa : il faut vérifier si ce modèle précis + votre CLI actuelle passe par le chemin Transducer/modified beam qui les supporte.

Mais si ton objectif est quelque chose du genre <50–80 Mio + contexte dynamique, alors Vosk devient vraiment intéressant comme troisième candidat. Le modèle français vosk-model-small-fr-0.22 fait 41 Mio, fonctionne explicitement sur Raspberry Pi, et les petits modèles permettent une reconfiguration dynamique du vocabulaire. 
Alpha Cephei
+1

Le problème est qu’en précision générique il part de plus loin : Vosk annonce environ 19–27 % WER suivant les datasets français pour ce petit modèle. 
Alpha Cephei
 Ce n’est donc probablement pas un remplaçant évident de ton Sherpa à 13,4 % WER. Mais avec un vocabulaire très contextualisé à Mycroft, il peut être beaucoup plus pertinent que ne le laisse penser son WER générique.

Et il existe une quatrième piste assez séduisante techniquement : Picovoice Leopard/Cheetah. Français, offline, Raspberry Pi, modèles annoncés <40 Mio, vocabulaire custom et keyword boosting. 
Picovoice
+1
 En revanche, ce n’est plus la même philosophie : moteur propriétaire, AccessKey Picovoice, customisation via leur console. Pour TANSTAFLLM, je serais réticent à mettre Mycroft au cœur du système dessus.

Du coup je verrais le benchmark v1 comme ça :

Candidat	Taille	Français	Context/hotwords dynamiques	FOSS	Intérêt Mycroft
Sherpa Zipformer actuel	~200 Mio	excellent	à vérifier / probablement possible selon modèle	oui	baseline qualité
Whisper Tiny q5_1	~38 Mio	moyen ici	prompt/grammar, mais pas vrai hotword biasing équivalent	oui	baseline taille
Vosk small-fr	41 Mio	oui	oui	oui	candidat très intéressant
Picovoice	<40 Mio annoncé	oui	oui, très bon support	non	référence technique

Whisper.cpp possède bien --prompt, --carry-initial-prompt et même un mécanisme de --grammar, donc dire « pas de contexte » serait un peu trop fort. 
GitHub
 Mais ça n'est pas exactement ce que j’attends de Mycroft. Pour toi, le besoin est plutôt :

Mike sait que l'écran actuel contient “GitHub / Wyoh / swaymsg / Codex” → il transmet cette petite liste à Mycroft → l'ASR augmente temporairement leur probabilité sans restreindre complètement ce que l'utilisateur peut dire.

Ça, c'est du contextual biasing dynamique, et c'est beaucoup plus intéressant qu'un simple prompt Whisper.

Donc je changerais même légèrement notre cahier des charges : le vrai sweet spot Mycroft n'est pas simplement “ASR <100 MB”. C'est “ASR ~40–80 MB + contextual vocabulary injectable à chaque utterance”.

Et à mon avis Vosk small-fr mérite maintenant absolument de passer dans votre harness. À 41 Mio et avec vocabulaire dynamique, c'est probablement le benchmark manquant le plus important. 
Alpha Cephei
+1

## Utilisateur

c'est quoi la taille typique du contexte ?

## Assistant

Pour du contextual biasing ASR, on parle généralement d’un contexte très petit par rapport à un LLM.

Typiquement, tu injectes plutôt :

10 à 50 mots/expressions pour un contexte très ciblé,

50 à 200 entrées pour un contexte applicatif riche,

parfois quelques centaines, mais au-delà ça commence à diluer le bias et à coûter en décodage.

Une “entrée” peut être un mot ou une expression entière : Wyoh, swaymsg, GitHub, ouvre le terminal, branche main, etc. En mémoire brute, c’est négligeable : même 200 expressions × 20 caractères, c’est seulement quelques kilo-octets. Le vrai coût vient du graphe/trie de décodage et de l’impact sur les probabilités, pas du stockage.

Pour Luna, je viserais quelque chose comme 30–100 entrées dynamiques par utterance. Par exemple : 10–20 noms visibles dans l’UI, 10 commandes possibles, quelques noms propres du projet, éventuellement 20–50 termes venant de l’application au premier plan.

Donc le scénario intéressant serait vraiment : Wyoh/Mike génèrent un mini lexique contextuel de quelques dizaines d’éléments, Mycroft le charge juste avant de décoder la phrase suivante. Ça reste suffisamment petit pour être très dynamique.

## Utilisateur

OK on va intégrer dans notre panel de candidats des très petits modèles à contexte et on fera par la suite un step sur l'intéret de la contextualisation.

## Assistant

Oui, ça me paraît être la bonne séquence.

Pour le panel de candidats ASR, on garde deux familles en parallèle : d’un côté les modèles “généralistes compacts” comme Sherpa/Whisper, et de l’autre des très petits modèles explicitement compatibles avec du contextual biasing / vocabulaire dynamique.

Le benchmark suivant doit donc répondre séparément à deux questions :

Sans contexte, quel est le meilleur compromis taille / RAM / vitesse / WER sur Luna ?

Avec contexte, combien gagne-t-on réellement sur le vocabulaire propre à TANSTAFLLM : Wyoh, Mycroft, Mike, swaymsg, noms d’applications, commandes visibles, etc. ?

Je formaliserais le critère de sélection comme : priorité aux candidats <100 Mio, avec un sous-groupe “ultra-small” <50 Mio, et support de contexte dynamique comme critère distinct, pas comme prérequis immédiat.

Ça évite de biaiser le benchmark initial tout en préparant proprement le step suivant sur la contextualisation.

## Utilisateur

dans un premier temps on peut garder Sherpa pour caler l'archi et les interfaces et penser la contrextualisation comme une optimisation

## Assistant

Oui. C’est même probablement la meilleure façon de découpler les risques.

On peut considérer Sherpa comme backend de référence pour Mycroft v0 : il est déjà suffisamment bon pour valider toute l’architecture — capture audio, normalisation 16 kHz mono, appel ASR, format de sortie, timestamps éventuels, IPC avec Mike/Wyoh, gestion des erreurs et latence.

Ensuite, la contextualisation devient une optimisation de backend, pas une propriété structurante de l’interface. L’interface Mycroft devrait donc dès maintenant prévoir quelque chose comme context/hints/hotwords en entrée, même si le backend Sherpa v0 l’ignore.

Ça donnerait conceptuellement :

audio + optional_context
        ↓
      Mycroft
        ↓
   ASR backend
        ↓
 transcript + confidence + metadata

Ainsi, quand on testera Vosk ou un très petit modèle contextualisable, on ne change pas l’architecture, seulement l’implémentation du backend.

Je garderais donc la décision suivante dans la doc : Sherpa = backend de bring-up / référence qualité ; contextualisation = optimisation v1 ; backend interchangeable dès v0.

## Utilisateur

Je vais parler un petit peu pour expliquer ce que je pense faire sur la saisie, enfin l'interface, l'interface vocale que je veux mettre en place. En fait, c'est pas tant de parler librement et que ça arrive directement, que ça se déverse. Je serai plus dans quelque chose, comme quand les Japonais tapent avec un clavier. C'est-à-dire qu'ils font des compositions, ils préparent et puis ils changent un peu la composition. Ils tapent des mots, ils choisissent des mots, etc. Et je suis plus dans cette idée-là. Tel que je l'imagine, c'est on va utiliser les boutons pour activer la capture vocale. Donc j'imagine, j'appuie un bouton, j'appuie sur un bouton de la Game Boy et comme ce que je fais actuellement avec ChatGPT, on se met en mode de saisie vocale et on peut dicter. On arrête. On a toujours le truc, on a toujours le texte qui a été dicté et là on peut l'altérer un petit peu. Sur la Game Boy, par exemple, on a deux petits joysticks, un à gauche, un à droite, et on peut s'imaginer que le joystick de gauche, il va me permettre de me déplacer mot après mot dans mon petit espace d'input, dans ma petite fenêtre de texte où j'ai mon input. Et pourquoi pas le deuxième joystick, ça serait pour switcher des mots ou des choses comme ça, interagir sur cette fenêtre de saisie. Et ça, ça pourrait être intéressant. Et donc si on a en plus quelque chose de riche qui provient de l'algorithme LLM, pas LLM, pardon, du modèle voice to text, du transformeur. Ça peut être, si on a des statistiques sur ce mot, qu'est-ce qu'il peut être ou pas. Peut-être qu'on pourrait s'en servir aussi pour switcher un mot. Ça, je dis ça, c'est très prospectif. Donc on peut le poser de côté. Par contre, ce qui peut être intéressant plus, c'est de se dire que quand j'ouvre ma fenêtre de saisie de texte, je pourrais choisir un mode. C'est-à-dire, imaginons, j'ai des boutons. J'ai plein de boutons sur cette Game Boy. Je pourrais avoir un bouton de saisie de texte, mais je sais pas, si j'appuie deux fois sur le bouton, ça passe à un autre mode. Je pourrais avoir un mode pour faire de la dictée au kilomètre, que je sais être destiné à un LLM sur API, à un Frontier LLM, et il n'y a pas de problème. Par contre, je peux avoir un mode pour exécuter une commande. Et donc là, on pourrait arriver sur une stratégie de il identifie, commence par identifier la commande, et ensuite il me propose des arguments ou il utilise des arguments en contexte. Quelque chose comme ça. Autre chose, c'est, voilà, à qui on s'adresse. Si on s'adresse à Mike, non, par exemple, on pourrait être dans un mode de navigation dans l'interface. C'est-à-dire que dans les différentes phrases que tu m'as fait lire, il y en a certaines qui concernent la navigation dans l'interface. Donc c'est ça. Par exemple, on pourrait avoir un truc tout con, c'est j'ai un bouton pour passer en mode de saisie de texte vocal. Si j'appuie plusieurs fois sur ce bouton, je change de mode, avec peut-être un code couleur, vert, c'est à destination du LLM pour faire du codage, bleu, c'est à destination du LLM pour faire de la discussion libre, jaune, c'est pour la ligne de commande, rouge, c'est pour la navigation dans l'interface, etc. Et donc là, si on fait ça, en fait, on va spécialiser notre cas d'usage. Et je pense que c'est là où l'histoire du modèle avec contexte prend tout son sens. Parce que quand on spécialise le cas d'usage, on restreint vraiment très fortement. Et donc, on cible le contexte, typiquement, si je fais une ligne de commande, c'est pas absurde que dans mon contexte, je passe les fichiers qui sont dans le répertoire courant. Si je suis en mode de navigation, c'est pas délirant de dire je vais lister les icônes qui sont visibles à ce moment-là sur le bureau ou le menu qui est à disposition à ce moment-là. Voilà. C'est ça que j'avais en tête et c'est pour ça que ça m'intéresse vraiment d'avoir des modèles à contexte.
Show less

## Assistant

Oui — là, le besoin devient beaucoup plus clair, et surtout la contextualisation n’est plus une optimisation marginale : elle devient une propriété naturelle de l’interface.

Ce que tu décris ressemble moins à de la « dictée vocale » qu’à un IME vocal — au sens des méthodes de saisie japonaises : la voix produit une proposition éditable, puis l’utilisateur compose, corrige, choisit et valide avant que le texte ne parte vers sa destination.

Je structurerais Mycroft autour de trois idées.

1. La transcription n’est jamais immédiatement une action

Le bouton déclenche une capture :

PRESS
  ↓
recording
  ↓
RELEASE / PRESS
  ↓
ASR
  ↓
┌───────────────────────────────┐
│ git checkout feature/mycroft  │
│              ^                │
└───────────────────────────────┘
       editing / selection
              ↓
          VALIDATE

La sortie de l’ASR devient donc un buffer de composition.

Ça change beaucoup de choses : un WER de 13 % n’est plus nécessairement dramatique si les erreurs sont simples à repérer et corriger. L’objectif du système devient plutôt :

minimiser l’effort nécessaire pour transformer l’hypothèse ASR en intention correcte.

Et tes deux sticks deviennent très intéressants. Par exemple, stick gauche = navigation par mot/segment ; stick droit = alternatives/corrections. Sans figer encore le mapping exact.

2. Le mode de saisie donne énormément de contexte avant même que tu parles

C’est probablement le point architectural le plus important.

Ton bouton vocal ne signifie pas seulement « écoute-moi ». Il signifie quelque chose comme :

Voice Input
   │
   ├── Chat / discussion
   ├── Frontier LLM / coding
   ├── Command
   └── UI navigation

Et chacun de ces modes peut définir un context provider différent.

Par exemple :

Mode	Destination	Contexte ASR possible
Chat	Mike / LLM	vocabulaire général + conversation
Coding	Frontier LLM	repo, fichiers, symboles, branche Git
Shell	terminal	commandes, cwd, fichiers, executables
Navigation	Wyoh	fenêtres, icônes, applications, actions disponibles

Ton exemple shell est particulièrement parlant. Supposons :

cwd = ~/git/tanstfaafllm

files:
README.md
docs/
mycroft/
wyoh/
src/

git branches:
main
feature/mycroft

Avant même que tu parles, Mycroft pourrait recevoir :

mode: shell

context:
  cd
  git
  checkout
  status
  docs
  mycroft
  wyoh
  feature/mycroft
  README.md

Si tu prononces :

« git checkout feature mycroft »

le modèle n’a plus à départager uniformément toutes les séquences phonétiquement plausibles du français. feature/mycroft existe ici et maintenant et reçoit donc un bias.

Même chose pour Wyoh. Si l’écran ne contient que :

Terminal
GitHub
Settings
Files

et que tu dis :

« ouvre GitHub »

le contexte est extraordinairement contraint.

3. Command mode permet d’aller encore plus loin

Là, ton idée de reconnaître d’abord la commande puis les arguments est probablement très puissante.

Ce n’est plus nécessairement :

audio
 → transcription complète
 → interprétation de la phrase

mais potentiellement :

audio
    ↓
 COMMAND ASR
    ↓
"open"
    ↓
expected argument:
APP
    ↓
context = visible applications
    ↓
"github"

Ou :

"checkout"
     ↓
expected:
GIT_BRANCH
     ↓
git branch --format ...
     ↓
feature/mycroft

Ça commence à ressembler à un dialogue avec une grammaire dynamique, plutôt qu'à de l'ASR généraliste.

Et c'est précisément là que des modèles beaucoup plus petits pourraient devenir compétitifs avec Sherpa : ils n'ont pas besoin de connaître parfaitement tout le français si, dans certains modes, l'espace des intentions admissibles est minuscule.

Je séparerais donc maintenant l'architecture en trois objets, pas simplement « Mycroft = ASR » :

                 ┌──────────────────┐
BUTTON / MODE ──►│ Input Controller │
                 └────────┬─────────┘
                          │
                    input mode
                          │
              ┌───────────▼───────────┐
              │   Context Provider    │
              │                       │
              │ Wyoh / cwd / git /    │
              │ apps / conversation   │
              └───────────┬───────────┘
                          │
                    hints/context
                          │
audio ────────────────────▼───────┐
                                  │
                           ┌──────▼──────┐
                           │   Mycroft   │
                           │     ASR     │
                           └──────┬──────┘
                                  │
                         hypotheses
                                  │
                         ┌────────▼───────┐
                         │  Composition   │
                         │    Buffer      │
                         │                │
                         │ words / alts / │
                         │ selection      │
                         └────────┬───────┘
                                  │
                              ACCEPT
                                  │
                         Mike / Wyoh /
                         shell / Frontier

Et surtout, je ne chercherais pas encore à implémenter toutes les idées prospectives.

Pour la V0, Sherpa peut parfaitement faire :

bouton → capture → Sherpa → texte → buffer éditable → validation → destination.

Le Input Controller, le mode et le context doivent par contre déjà exister dans les interfaces, même si :

context = []
alternatives = []

au début.

Ensuite on pourra faire un vrai Mycroft contextualization experiment : reprendre exactement les mêmes phrases et mesurer successivement generic ASR → mode context → environment context → structured command context.

Ça pourrait produire un résultat bien plus intéressant qu'un simple benchmark de WER : mesurer combien de modèle on peut enlever grâce à la connaissance de l'état du système.

Et ça colle particulièrement bien à Luna : contrairement à un assistant vocal dans une pièce, Luna connaît énormément de choses sur ce que l’utilisateur est susceptible de vouloir faire à cet instant précis.

## Utilisateur

Autre idée, autre idée. On est en plein dans la hype de JEV, J-E-V, qui est un espèce de, comment dire, de classifier, ou de, oui, de classifier fermé, de machine probabiliste, qui permet de donner des poids probabilistes sur des options, sur un périmètre fermé à chaque fois. Je me disais sur la partie, par exemple, exécution de command line. Imaginons, voilà, le voice to text est passé, voice to text est passé, il fait une première proposition. En fait, on pourrait proposer des transformations par rapport à un, comment dire, à un ensemble fermé d'options, parce que peut-être qu'on peut choisir en disant, est-ce que c'est une commande ou pas ? Est-ce que c'est de la navigation dans les sous-répertoires, que sais-je ? Enfin voilà, essayer d'utiliser ce genre de modèle, qui sont basés sur des BERT, pour faire des choses comme ça, c'est-à-dire arriver sur un ensemble d'options fermé qu'on va venir traiter de manière extrêmement rapide et extrêmement efficace avec des modèles que vous. Alors effectivement, en ce moment, JEV, c'est un modèle à API, mais là, c'est la folie furieuse. On voit clairement que potentiellement, en manipulant bien deux, trois, un BERT bien senti, on va arriver à faire un JEV-like, un JEV-like qui va pouvoir tourner sur du matériel à la pas cher. Et donc, je me dis, voilà, ça c'est peut-être ça. C'est-à-dire que si on a cette fenêtre de saisie un peu collaborative, je fais une saisie vocale et j'ai des méthodes très rapides pour affiner, peut-être qu'un modèle secondaire comme ça, avec un ensemble de choix probabilistes fermés, serait pas mal. Et voilà. On le met dans la boîte à idées. Je pense que ça serait bien d'avoir une boîte à idées par ligne de travail. Donc on n'a qu'à dire qu'on met ça dans la boîte à idées de Mycroft. Du coup, quand même, juste. Mycroft, c'est pas juste un modèle speech to text. Mycroft, c'est le point d'entrée, le point d'entrée dans notre système. Et donc, voilà, le concept speech to text plus interface, plus interacteur rapide, plus peut-être des modèles annexes. Je me dis, ça pourrait être ça Mycroft. Et donc c'est vraiment quelque chose de testable, etc. Je clique sur des boutons, ça ouvre la fenêtre. Je parle un peu, ça me saisit, ou je relâche le bouton, ou j'appuie sur un autre bouton, ça se termine. Ça analyse le texte que j'ai préparé, avec son contexte, ça me fait deux-trois propositions, ça pourrait être un truc comme ça, ça me fait quelques propositions, et je choisis la proposition. Et on serait pas mal.
Show less

## Assistant

Oui, je vois exactement le pattern — et Jev est bien le type de modèle auquel tu penses : un modèle qui prend un état/contexte et répond sur des questions fermées avec une distribution de probabilités, plutôt que de générer du texte libre. Leur API expose notamment Choice, Score et Noul (oui/non probabiliste). 
Jev Model
+1

Pour Mycroft, ça donne une architecture beaucoup plus intéressante qu’un simple pipeline ASR.

Le principe pourrait être :

VOICE
  ↓
ASR
  ↓
"git check out feature mycroft"
  ↓
Mycroft composition buffer
  ↓
small decision models
  ├─ intent: shell / navigation / prose / coding
  ├─ operation: git / filesystem / process / other
  ├─ command candidate ranking
  └─ argument candidate ranking
  ↓
2–4 structured proposals
  ↓
user selects / edits / validates

Et le point essentiel est que les modèles secondaires n'ont pas besoin d'être génératifs.

Par exemple, sur :

« ouvre le dossier mycroft »

on pourrait poser localement quelque chose d’équivalent à un Choice :

intent:
  - shell_command
  - ui_navigation
  - text_input
  - llm_request

puis, si shell_command gagne :

operation:
  - cd
  - ls
  - mkdir
  - open
  - other

et ensuite exploiter le contexte réel :

cwd:
  docs/
  mycroft/
  wyoh/
  tests/

pour produire quelques candidats :

cd mycroft/
xdg-open mycroft/
cd docs/mycroft/

avec, idéalement, des poids.

C'est précisément là qu'un petit BERT / MiniLM / DistilBERT quantifié, voire plusieurs modèles spécialisés ridiculement petits, devient très séduisant. On n'a pas besoin d'un « cerveau » généraliste : on veut répondre extrêmement vite à des questions du type A/B/C/D à partir de quelques dizaines de tokens.

Il y a même un joli découpage conceptuel :

              MYCROFT
                 │
 ┌───────────────┼────────────────┐
 │               │                │
Audio          Context          Controls
 │               │                │
 ▼               ▼                ▼
 ASR        system state       buttons/sticks
 │               │
 └───────┬───────┘
         ▼
 Composition Buffer
         │
         ▼
 ┌───────────────────────┐
 │ Fast decision layer   │
 │                       │
 │ intent classifier     │
 │ candidate ranker      │
 │ confidence estimator  │
 │ transformation chooser│
 └───────────┬───────────┘
             │
       proposals
             │
             ▼
       human selection
             │
             ▼
 Mike / Wyoh / shell / Frontier

Et je suis d'accord avec ta redéfinition : Mycroft n'est plus le speech-to-text.

Je le définirais maintenant comme :

Mycroft is Luna's interactive input and composition system. It combines voice recognition, system context, lightweight decision models and physical controls to turn imperfect human input into an explicit, reviewable intent before execution.

C'est beaucoup plus fort comme concept.

Et surtout, il y a une conséquence architecturale que j'aime beaucoup : Mike n'a pas besoin d'intervenir dans chaque interaction. Pour une énorme quantité d'actions triviales, le chemin peut rester entièrement local :

speech
→ 40–200 MB ASR
→ 10–50 MB classifier/ranker
→ user confirms
→ command

Pas de LLM frontier, potentiellement pas de LLM du tout.

Pour ta boîte à idées Mycroft, je mettrais donc déjà ces entrées :

Voice IME / composition buffer : transcription non exécutée immédiatement, éditable et validable.

Input modes : conversation, coding/frontier, shell, navigation, etc.

Contextual ASR : contexte dérivé du mode et de l'état courant.

Alternative word selection : utiliser éventuellement les hypothèses/n-best de l'ASR pour corriger au joystick.

Jev-like local decision layer : petits modèles fermés donnant des probabilités sur intents/actions/transformations.

Hierarchical classification : déterminer successivement intent → action → arguments plutôt qu'un énorme espace de classes.

Candidate generation + ranking : construire des actions possibles à partir de l'état réel de Luna, puis les classer.

Human-in-the-loop by design : présenter 2–3 propositions rapides plutôt que chercher systématiquement une interprétation automatique parfaite.

Confidence-driven UX : si une proposition est écrasante, UI minimale ; si les scores sont proches, montrer explicitement plusieurs choix.

Local-first fast path : exécuter les tâches simples sans Mike ni Frontier LLM.

Et ton intuition sur Jev est intéressante pour une autre raison : Jev lui-même insiste justement sur les espaces de choix prédéfinis et les distributions de probabilité, avec possibilité d'ajouter une option other/none-of-the-above pour gérer l'incertitude. 
GitHub

Donc lorsqu'on en viendra à prototyper cette couche, le bon objectif ne sera probablement pas « reproduire Jev ». Ce sera plutôt :

identifier les 3 ou 4 primitives Jev-like dont Mycroft a réellement besoin et voir jusqu'où on peut aller avec de minuscules modèles locaux.

Ça, sur un RK3326, pourrait devenir une ligne de R&D vraiment intéressante à elle seule.

If you want, I can:

Proposer une couche décisionnelle Jev-like pour Mycroft

Détailler comment utiliser les joysticks pour éditer le buffer vocal

Développer la gestion multi-mode dans Mycroft avec code couleur

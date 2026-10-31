# Mike harness and zero-shot decider — raw ChatGPT export

> **Freshness:** 🟢 current · **Written:** 2026-10-19 · **Checked:** 2026-10-31 · **Step:** mike 7 ⏳

> Source : https://chatgpt.com/share/6ace95fc-0800-83eb-bd5f-9d86b7257744  
> Captured with `scripts/scrape_shared_chat.py` (kept-longest-text fix of 2026-10-13). One user message before the assistant message on Mike/Mannie memory modes was not captured (the user does not remember it). Cleaned record: `0700_02_harness-and-decider-discussion.md`.
> Export Playwright le 2026-10-13 — 77 messages.

## Utilisateur

Je pense qu'aussi il faudra à terme pour Mike faire un tour sur les JEV-like, JEV, J-E-V, parce que c'est des modèles décisionnels fermés, donc modèles décisionnels fermés, one-shot, promptable. Euh, pas one-shot, zéro-shot, pardon, promptable. Et ça potentiellement, c'est très intéressant. C'est-à-dire que moi, quand je fais une commande, quand je fais une commande de type ouvre-moi, liste les fichiers dans mon dir, ben j'ai quand même, j'ai quand même, quand j'envoie à Mike, première étape, c'est à quelle application c'est destiné. Est-ce que c'est une ligne de commande, est-ce que c'est un machin, etc. Donc j'ai potentiellement un nombre de choix fermés à faire. Dans le sens où je vais pas demander à Mike de faire ce que fait Claude, c'est-à-dire de faire un plan et de composer des opérations. Mike, il doit faire une action à la fois. Je lui donne un ordre, il le fait. Ou je donne un ordre et il le convertit en du texte et il le balance sur l'input. Mais Mike, il va pas faire un plan et faire un ensemble d'opérations complexes et tout. Alors, je dis ça. Bon, si je lui demande d'aller ouvrir une application, je sais pas. Je m'interroge encore sur les capacités de Mike. Dans tous les cas, il va falloir lui trouver un harness. Et ça, j'aimerais bien avoir des propositions.

## Assistant

Je pense que la piste JEV est particulièrement pertinente pour Mike, et qu'elle pourrait même nous amener à revoir sa conception.

Jusqu'ici, on cherche un petit LLM suffisamment intelligent pour produire un appel d'outil. Mais tu proposes autre chose : Mike serait essentiellement un moteur de décision sur un ensemble fermé d'actions, plutôt qu'un agent conversationnel miniature.

Et c'est assez cohérent avec le principe de TANSTAAFLLM : utiliser le minimum d'intelligence nécessaire.

1. Pourquoi JEV mérite d'être testé

J'ai retrouvé Jev Model et son approche System One, ainsi que le projet 
JevEmbed
.

JEV prend un état et des questions typées, puis retourne des décisions structurées plutôt que de générer un texte libre. Trois types de sorties sont proposés :

Type

	

Exemple pour Mike




Choice

	

Terminal, application, action système ou refus




Noul (oui/non)

	

La commande nécessite-t-elle une confirmation ?




Score

	

Quel degré de risque ou d'ambiguïté ?

Les choix peuvent être décrits en langage naturel à l'exécution. On peut donc changer les possibilités sans nécessairement réentraîner un classifieur. 
jevmodel/jev-ai: Jev Model · GitHub
+2

Il y a toutefois une réserve essentielle : le JEV original est proposé comme service distant. Il ne constitue pas encore une solution locale démontrée sur Luna. Pour cela, il faut examiner les implémentations ouvertes, leurs poids, leurs runtimes et leur empreinte réelle.

2. Mike n'a pas forcément besoin de générer du texte

Je distinguerais trois capacités :

Niveau 1 — Décider

Identifier une intention, choisir une application ou une action parmi une liste fermée.

JEV-like

Niveau 2 — Renseigner

Extraire ou résoudre les paramètres : répertoire personnel, nom d'application, nom de fichier.

Règles + contexte

Niveau 3 — Produire

Construire une expression non prévue par les règles : commande shell, texte à injecter, argument complexe.

Petit LLM si nécessaire

Par exemple, « liste les fichiers dans mon home » :

Le décideur identifie terminal.list_directory.

Le résolveur reconnaît home et le traduit en répertoire personnel.

Un adaptateur produit ls ~.

Aucune génération libre n'est nécessaire.

En revanche, « écris une expression régulière qui retrouve tous les fichiers de log datés » demande une capacité de génération. C'est là qu'un petit LLM peut reprendre la main, ou que la demande doit être escaladée.

Je ne supprimerais donc pas LFM2.5-350M. Je chercherais à réduire considérablement les situations dans lesquelles on doit l'invoquer.

3. Trois architectures de harness possibles

Je proposerais de comparer trois approches, avec le même banc d'essai.

A. Harness déterministe + LFM2.5-350M

Le plus proche du travail déjà réalisé. Une table de règles traite les commandes simples ; le LLM fournit un appel d'outil JSON contraint. Un adaptateur vérifie les arguments, demande confirmation et traduit l'action en IPC Sway. llama.cpp prend en charge les grammaires GBNF et les sorties contraintes par schéma JSON. 
GitHub
+1

Avantage : réutilisation maximale de l'existant. Inconvénient : poids du modèle et génération de tokens.

B. Harness décisionnel JEV-like

Un modèle de classification choisit une action parmi les capacités actuellement disponibles dans Wyoh. Des résolveurs déterministes fournissent les arguments. Les commandes inconnues sont refusées ou transférées à un modèle génératif.

Le candidat à étudier est JevEmbed, notamment ses implémentations utilisant des modèles d'embeddings. GLiClass est également une piste pour la classification zero-shot sur CPU. 
GitHub
+1

Avantage : sortie fermée, potentiellement peu de calcul. Inconvénient : résolution des paramètres, langues et mémoire encore à qualifier sur ARM.

C. Harness hybride à intelligence progressive

Routeur déterministe → modèle décisionnel → résolveur de paramètres → LLM génératif uniquement si nécessaire.

Tous utilisent le même catalogue d'actions et les mêmes règles de validation. Aucune boucle de planification autonome.

Avantage : séparation nette des responsabilités et coût ajusté à chaque requête. Inconvénient : davantage de composants à maintenir et, s'ils restent chargés ensemble, potentiellement plus de RAM.

Je privilégierais C comme architecture cible, mais je commencerais par A : c'est le meilleur moyen de valider le harness sans attendre de qualifier un deuxième modèle. Puis on remplace progressivement les décisions génératives par un JEV-like si les benchmarks le justifient.

4. Le micro-harness que je construirais

Je garderais cinq modules seulement.

Slate → Mike

Énoncé + application ciblée + contexte Wyoh

1. Context

Fenêtre, capacités, focus

2. Router

Règles / JEV / LLM

3. Resolver

Paramètres et commandes

4. Policy

Validation, refus, confirmation

5. Executor

IPC Sway / MCP Wyoh / injection de texte

Le principe central : une requête de Mike produit au maximum une action.

L'executor peut éventuellement récupérer un résultat pour l'afficher, mais il ne renvoie pas ce résultat au modèle pour lui demander de décider de l'étape suivante. Pas de boucle ReAct, pas de planificateur, pas d'agent autonome.

C'est une frontière beaucoup plus simple à sécuriser, tester et maintenir.

Un contrat minimal
JSON
{
  "action": "terminal.list_directory",
  "args": {
    "path": "home"
  },
  "target": "focused_terminal"
}

Le harness traduit en ls ~, affiche la commande proposée et laisse l'utilisateur confirmer son insertion ou son exécution.

Pour les actions reconnues, on n'autorise pas le modèle à produire librement du shell. La traduction est déterministe. Pour les demandes hors catalogue, Mike peut répondre unsupported plutôt que d'inventer une commande.

5. Comment qualifier les candidats

Ton dépôt possède déjà 81 demandes principales et 31 demandes held-out pour Mike. C'est un bon point de départ, même si les scores actuels ne permettent pas encore de conclure sur la capacité du modèle à agir dans différents contextes.

Je ferais le benchmark suivant :

Mesure

	

Ce qu'on cherche




Exactitude du routage

	

Bonne action, bonne application




Exactitude des arguments

	

Bon fichier, bon chemin, bonne cible




Rejet hors domaine

	

Pas d'action inventée




Latence sur Cortex-A35

	

Temps de décision acceptable




RAM résidente

	

Coût réel sur Luna




CPU au repos

	

Capacité à rester disponible




Français oral

	

Robustesse aux formulations issues de Mycroft

Et surtout, je séparerais les tests de classification pure des tests de composition de commande. Autrement, on risque de rejeter un excellent décideur simplement parce qu'il ne sait pas générer du shell — alors que cela n'est pas sa fonction.

6. Une limite de JEV à garder en tête

Il ne faut pas confondre sortie fermée et action correcte.

Un modèle JEV-like peut choisir très efficacement parmi launch_app, list_windows, focus_window, terminal_command, etc. Mais il faut toujours résoudre les paramètres, traiter les cas ambigus, contrôler l'autorisation de l'action et gérer ce qui se passe lorsqu'aucun choix ne convient.

Et, autre point, les scores ou probabilités de décision ne doivent pas être considérés comme automatiquement calibrés. Le taux de refus doit être réglé sur un jeu de tests représentatif.

Pour l'instant, JevEmbed propose notamment des configurations basées sur Qwen3-Embedding-0.6B : intéressant conceptuellement, mais pas nécessairement plus petit que le LFM2.5-350M retenu. Il faudra chercher des bases d'embeddings sensiblement plus petites pour que cette piste soit intéressante sur Luna. 
GitHub
+1

La décision structurante que je retiendrais pour Mike est donc celle-ci :

Mike n'est pas un Claude miniature. C'est un contrôleur local à actions bornées, capable de comprendre une instruction, de choisir une opération, de renseigner ses arguments et de soumettre une seule action.

Le harness doit être indépendant du modèle : aujourd'hui LFM2.5, demain JEV-like, ou un ensemble des deux.

C'est probablement la bonne direction pour tirer parti des quatre Cortex-A35 sans transformer le projet en course à la taille des LLM.

## Utilisateur

On va quand même séparer rapidement GF du harness. Et quand je dis harness, c'est surtout, je veux faire demain un petit agent. Mais un petit agent, ça a plein de choses. C'est pas juste un LLM et c'est pas juste un chat. C'est vraiment le fait de pouvoir utiliser des skills, le fait d'avoir une memory, le fait de pouvoir, comment dire, faire des actions, utiliser des tools, etc. Donc moi, je voudrais voir qu'est-ce que j'ai à disposition qui pourrait me permettre de faire un agent avec un petit modèle. Donc, est-ce qu'il y a des gens qui ont commencé à faire ça, des petits agents sur des petits agents en BD, ce genre de choses.

## Assistant

Oui, là on parle d'un sujet différent de JEV : trouver un véritable runtime agentique, mais adapté à un modèle de 350 millions de paramètres et à une machine de 1 Go de RAM.

Un agent, même très petit, doit disposer d'un environnement d'exécution : outils, skills, mémoire, contexte, sessions, permissions et éventuellement boucles d'utilisation d'outils. Le modèle n'est qu'un composant interchangeable.

J'ai trouvé plusieurs projets qui vont précisément dans cette direction. Et il y en a un particulièrement intéressant pour Luna : PicoClaw, un agent écrit en Go et conçu pour des machines embarquées.

1. Les candidats qui méritent un examen

PicoClaw

Priorité 1

Go · Agent embarqué · Binaire natif

Annonce une empreinte de moins de 10 Mo pour son runtime, avec une architecture destinée aux appareils ARM et RISC-V. Il fournit un environnement d'agent et des outils, tout en déléguant l'inférence à un fournisseur de modèles. C'est le candidat le plus directement aligné avec les contraintes matérielles de Luna. 
GitHub
+1

ZeroClaw

Rust · Runtime compact · Modules interchangeables

Un autre candidat sérieux. Il annonce une empreinte de quelques Mo, des providers interchangeables, des outils et des contrôles de sécurité. Son architecture paraît particulièrement intéressante pour isoler le moteur d'inférence des capacités de l'agent. Les chiffres d'empreinte restent à reproduire. 
GitHub
+1

NanoBot

Python · Skills · Mémoire · MCP

Plus proche d'un agent personnel complet : outils, mémoire persistante, skills, sessions, intégrations MCP et automatisations. Il est plus lourd conceptuellement et probablement moins intéressant à installer tel quel sur Luna, mais constitue une excellente référence fonctionnelle. 
GitHub
+1

MicroClaw

Rust · SDK embarquable · Agent persistant

Dispose d'un SDK réutilisable, de la mémoire SQLite, des skills, d'un moteur d'outils, de MCP et de politiques d'exécution. Plus ambitieux que Mike, mais intéressant pour étudier les frontières entre agent, outils et persistance. 
GitHub
+1

PocketFlow

Python · Environ 100 lignes · Graphe d'exécution

Extrêmement minimal, sans dépendances, mais ce n'est pas un harness complet : il faut fournir soi-même mémoire, catalogue d'outils, skills et politiques. Intéressant si l'on choisit finalement de construire un runtime spécifique à Luna. 
GitHub
+1

La nuance importante : un agent dont le runtime consomme 10 Mo n'est pas nécessairement un agent dont le modèle tourne localement. Beaucoup de ces projets sont d'abord conçus pour appeler des API distantes. Pour Mike, il faudra vérifier leur compatibilité avec un backend llama.cpp local, et surtout leur capacité à travailler avec un très petit modèle.

2. Comparaison du point de vue d'un vrai agent

Voici les capacités qui comptent, indépendamment de la taille du modèle.

Projet

	

Tools / MCP

	

Skills

	

Mémoire

	

Adaptation à Luna




PicoClaw

	

Oui

	

Oui

	

Persistante

	

Très prometteur




ZeroClaw

	

Oui

	

Oui

	

Persistante

	

Très prometteur




NanoBot

	

Oui

	

Oui

	

Long terme

	

Référence fonctionnelle




MicroClaw

	

Oui

	

Oui

	

SQLite et fichiers

	

SDK intéressant




PocketFlow

	

À construire

	

À construire

	

À construire

	

Excellent socle minimal

Il s'agit des capacités annoncées par les projets, pas de fonctionnalités vérifiées sur le R36 Ultra.

PicoClaw est particulièrement intéressant : son README confirme un support MCP natif, du routage de modèles et des builds ARM. Il précise aussi que les versions récentes utilisent plutôt 10 à 20 Mo de RAM, et avertit que le projet est encore jeune. 
GitHub

3. Ce que cela pourrait donner pour Mike

Plutôt que d'écrire notre propre harness avant d'avoir étudié l'existant :

Slate / Wyoh

Entrée vocale, contexte utilisateur

Mike — Agent Runtime

PicoClaw ou ZeroClaw adapté

Skills

Memory

Tools / MCP

Session

Policy

Context

LFM2.5-350M

llama.cpp · modèle local interchangeable

Le harness gère ce que le modèle ne sait pas gérer seul.

Par exemple, une skill terminal pourrait décrire les commandes autorisées, leur syntaxe, les outils disponibles et les règles de confirmation. La mémoire retiendrait les préférences ou les derniers emplacements utilisés. Le catalogue d'outils serait construit à partir des capacités de Wyoh.

Le point délicat avec 350M paramètres ne sera sans doute pas l'exécution des outils par le harness, mais la capacité du modèle à utiliser correctement la description des outils et les instructions contenues dans les skills. Il faudra probablement limiter le nombre de capacités présentées simultanément.

4. Le benchmark que je ferais

Je sélectionnerais PicoClaw et ZeroClaw, et NanoBot comme référence fonctionnelle.

Je mesurerais d'abord le runtime sans modèle, puis avec le même LFM2.5-350M derrière une interface locale. Cela permettrait de mesurer séparément le coût du harness et les difficultés liées au petit modèle.

Les cinq scénarios de validation seraient : mémoriser une préférence puis la rappeler ; découvrir et utiliser un outil Wyoh ; charger une skill terminal ; conserver le contexte entre deux demandes ; demander une confirmation avant une opération sensible.

Je testerais également la possibilité de limiter un tour d'agent à une seule action, tout en conservant sa mémoire et ses skills. L'objectif n'est pas de faire de Mike un planificateur autonome, mais de lui donner les capacités d'un agent sans lui imposer toute la complexité d'un Claude Code.

Ma shortlist est donc PicoClaw, ZeroClaw et NanoBot. PicoClaw est le premier que j'examinerais réellement, et ce serait une bonne piste pour une nouvelle étape de recherche dans la workline Mike, sans rien implémenter pour l'instant.

Le sujet à trancher après ce premier benchmark sera moins « quel framework est le plus léger ? » que « lequel sait faire fonctionner un véritable agent avec un modèle de seulement 350M ? ». Ce sont deux problèmes très différents.

## Utilisateur

Entre PicoClos et ZeroClos, qu'est-ce qu'il y aurait comme réelle différence et qu'est-ce qui pourrait orienter le choix ? Au final, s'il n'y a pas de différence, le choix, c'est le dynamisme du projet et sa pérennité.

## Assistant

À ce stade, je donnerais un léger avantage à ZeroClaw pour construire Mike, mais PicoClaw conserve un avantage pour l'embarqué pur.

La différence n'est pas tant Go contre Rust, ni même 10 Mo contre quelques Mo. Les deux sont suffisamment légers pour Luna. La vraie distinction est leur philosophie : PicoClaw privilégie l'agent compact qui fonctionne partout ; ZeroClaw propose une infrastructure agentique plus structurée, avec une gestion explicite des capacités, des permissions et des modèles locaux.

Et sur ton critère de pérennité, les deux projets ont déjà une communauté significative.

1. Comparaison pour TANSTAAFLLM

Critère

	

PicoClaw

	

ZeroClaw




Langage

	

Go

	

Rust




Positionnement

	

Agent ultra-léger embarqué

	

Runtime agentique modulaire




Mémoire du harness

	

10–20 Mo annoncés pour les builds récents

	

Quelques Mo annoncés selon configuration




Modèle local

	

Ollama / API compatibles

	

Provider dédié llama.cpp, Ollama




Tools / MCP

	

Oui

	

Oui




Skills

	

SKILL.md

	

Skills et bundles de capacités




Mémoire

	

Fichiers et JSONL

	

SQLite, embeddings




Permissions

	

Contrôles d'outils, hooks

	

Profils de risque, approbations, sandbox




Petit modèle

	

Routage par règles

	

Profil spécifique local_small




Compatibilité ARM64

	

Oui

	

Oui, sous réserve de vérifier le build




Extensibilité

	

Go, assez direct

	

Architecture Rust en crates

GitHub
+3
2. Les trois différences qui comptent réellement
A. ZeroClaw prend explicitement en compte les petits modèles locaux

C'est le point qui me fait pencher vers lui.

Sa documentation contient un profil local_small, prévu pour limiter les prompts, l'historique et certains comportements de la boucle d'outils.

Il dispose également d'un provider natif llamacpp, avec une API locale par défaut sur localhost:8080/v1. 
GitHub
+1

Pour Mike, qui doit fonctionner avec LFM2.5-350M, c'est précieux. Cela ne garantit pas que le modèle saura appeler les outils, mais montre que le problème est identifié dans la conception.

PicoClaw propose aussi le routage vers des modèles locaux, mais sa documentation est davantage centrée sur la portabilité et les providers.

B. ZeroClaw a une politique d'exécution plus structurée

ZeroClaw distingue notamment les modes readonly, supervised et full, avec des politiques propres aux outils, des listes d'autorisation et des mécanismes de sandboxing. 
GitHub
+1

Cela correspond bien à ton usage de Mike : interpréter une demande, proposer une action et contrôler son exécution.

PicoClaw possède également des protections, des hooks et des politiques d'exécution, mais son propre projet indique que le durcissement de la sécurité est encore un chantier prioritaire. 
GitHub
+1

C. PicoClaw est plus directement orienté matériel très contraint

PicoClaw a été créé précisément pour fonctionner sur des machines embarquées extrêmement petites, jusqu'à des SBC RISC-V à très faible mémoire.

Sa feuille de route vise un processus principal sous les 20 Mo sur des cartes de 64 Mo. L'optimisation des ressources reste une priorité explicite. 
GitHub
+1

ZeroClaw revendique lui aussi une faible empreinte, mais développe une infrastructure beaucoup plus riche. Le risque est davantage celui d'une complexification progressive du produit.

Sur Luna, la différence de RAM entre ces deux harness sera vraisemblablement secondaire par rapport aux centaines de Mo de Mike et Mycroft, à condition de le confirmer par mesure.

3. Dynamisme et pérennité : les deux projets sont sérieux

PicoClaw

30k
Stars GitHub

4,4k forks

2 584 commits affichés

Initiative de Sipeed, fabricant de matériel embarqué

ZeroClaw

33k
Stars GitHub environ

5k forks environ

480 contributeurs recensés

Organisation communautaire ZeroClaw Labs

Ordres de grandeur visibles sur GitHub lors de la consultation, susceptibles d'évoluer. 
GitHub
+1

PicoClaw a un avantage intéressant en matière de pérennité : Sipeed vend réellement du matériel embarqué. Son intérêt pour un runtime qui tourne sur de très petites machines est donc cohérent avec son activité commerciale.

ZeroClaw bénéficie de son côté d'une communauté importante, d'un processus RFC, d'une architecture contributive modulaire et d'un rythme de publications soutenu. Une version v0.8.5 était notamment publiée le 5 septembre 2026. 
GitHub
+1

Je ne vois pas de vainqueur évident sur la seule popularité. Les deux ont dépassé le stade du petit projet isolé, sans que cela garantisse pour autant leur maintenance à long terme.

4. Le test qui départagerait réellement les deux

Je ne lancerais pas un benchmark général de tous leurs outils. Je ferais un test très ciblé sur le besoin de Mike.

Même modèle LFM2.5-350M, même llama.cpp, même serveur MCP Wyoh, et quatre scénarios :

Ouvrir une application depuis une instruction en français.

Charger une skill terminal puis proposer ls ~ à partir d'une commande en langage naturel.

Mémoriser une préférence, redémarrer l'agent et la retrouver.

Refuser ou faire confirmer une opération non autorisée.

Il faudrait mesurer RAM, taille de contexte injectée, latence, fiabilité des appels d'outils et quantité de modifications nécessaires.

J'insisterais particulièrement sur la taille des prompts système, les descriptions de tools et le chargement des skills. Un harness à 10 Mo qui injecte des milliers de tokens supplémentaires à chaque requête peut être bien moins efficace qu'un harness à 25 Mo.

C'est d'ailleurs un problème concret documenté pour certaines configurations de ZeroClaw : l'injection intégrale des skills peut fortement pénaliser le temps de préremplissage du contexte. 
GitHub

5. Mon choix provisoire

Je choisirais ZeroClaw comme premier candidat à expérimenter, pour trois raisons : l'intégration spécifique à llama.cpp, le profil dédié aux petits modèles et les politiques d'approbation des outils.

Mais je ne l'adopterais pas encore définitivement. PicoClaw me semble particulièrement bien placé pour rester maintenu sur les architectures embarquées, et son empreinte est très attractive.

Le véritable critère éliminatoire serait simple : si ZeroClaw nécessite de charger trop de contexte agentique pour que LFM2.5-350M fonctionne correctement, alors PicoClaw peut devenir le meilleur choix, même avec moins de fonctionnalités.

Autrement dit, je privilégierais le framework qui impose le moins de complexité au modèle, et pas seulement celui qui consomme le moins de RAM.

C'est à mon avis la bonne manière de choisir le futur harness de Mike.

## Utilisateur

C'est quoi la taille de notre contexte sur LFM2.5 ?

## Assistant

Sur notre LFM2.5-350M, la fenêtre de contexte théorique est de 65 536 tokens (64K). C'est également le cas du LFM2.5-230M.

Mais il faut distinguer la capacité maximale du modèle de la taille de contexte réellement configurée dans llama.cpp.

Sur Luna, c'est surtout cette deuxième valeur qui nous intéresse : la mémoire du KV cache augmente avec le contexte alloué, même si celui-ci n'est pas entièrement utilisé.

Pour Mike, je viserais plutôt 2K à 4K tokens de contexte actif au départ.

Cela laisse de la place pour le prompt système, les descriptions des tools, une skill et un historique court, sans mobiliser inutilement la RAM.

Contexte

	

Usage envisagé




1K

	

Routage d'une action simple




2K

	

Routage + quelques tools




4K

	

Petit agent avec skill et mémoire courte




8K

	

Plusieurs skills ou davantage d'historique




64K

	

Maximum théorique, peu pertinent sur Luna

Le dépôt confirme le modèle retenu et ses mesures mémoire, mais je n'ai pas retrouvé la valeur exacte de n_ctx utilisée dans les benchmarks.

Pour comparer PicoClaw et ZeroClaw, je testerais donc les deux à 4K, puis à 8K pour vérifier la dégradation de latence et de mémoire.

## Utilisateur

Est-ce qu'on a des blogs, des publications, des choses qui feraient une comparaison entre les deux ?

## Assistant

Oui, et j'ai trouvé nettement mieux qu'un simple comparatif de blog : une publication expérimentale qui teste précisément PicoClaw et ZeroClaw sur un Raspberry Pi 4, avec le même modèle pour isoler le coût du harness.

C'est particulièrement pertinent pour TANSTAAFLLM.

1. La publication à lire en priorité

Benchmarking Lightweight AI-Agent Frameworks on a 2 GB Raspberry Pi 4

Sajana Yasas Dehigaspitiyage Don · 8 juin 2026 · Prépublication sur Zenodo

Comparaison reproductible de ZeroClaw, PicoClaw, NanoBot et smolagents : mémoire, latence, exécution d'outils, mémoire persistante et inférence locale. 
Zenodo

Code, scripts et résultats bruts du benchmark

Les résultats mesurés
PicoClaw
Mémoire maximale
31 Mo
0 Mo
35 Mo
70 Mo
105 Mo
140 Mo
ZeroClaw
PicoClaw
smolagents
NanoBot

Pic RSS approximatif mesuré sur Raspberry Pi 4, 2 Go, avec modèle distant. Le runtime d'inférence local n'est pas inclus.

Le papier apporte deux enseignements :

ZeroClaw est plus léger que PicoClaw, mais la différence n'est que d'environ 11 Mo dans ces conditions. Sur Luna, elle ne suffit pas à orienter le choix.

L'inférence locale est le vrai obstacle. Les quatre frameworks échouent à leur test élémentaire avec un modèle local : Qwen2.5-1.5B est trop lent pour les timeouts par défaut ; SmolLM2-360M est assez rapide mais ne sait pas correctement appeler les outils.

Les expériences locales ne comportent que huit combinaisons modèle/framework, sur une tâche élémentaire. Ce n'est donc pas une preuve d'impossibilité, mais cela confirme précisément le risque que nous avions identifié pour Mike. 
Zenodo
+1

C'est le papier que je lirais avant de choisir un harness, d'autant que son code et ses données sont publiés.

2. Les autres comparatifs intéressants

AI Agent Frameworks Compared — Wael Mansour

10 mars 2026 · Lecture 12 min

Une revue relativement approfondie de l'écosystème OpenClaw, PicoClaw, ZeroClaw et NanoClaw. L'angle principal est la sécurité, l'isolation des outils et la simplicité architecturale, plutôt que les performances.

Intérêt pour Luna : comprendre ce que gagne ZeroClaw en matière de contrôle d'exécution. 
Wael Mansour

ZeptoClaw — comparaison de cinq frameworks

26 février 2026 · Analyse du code source

Très intéressant pour comparer les fonctionnalités, les outils, les dépendances et la complexité des différentes implémentations. C'est une analyse produite par un projet concurrent, donc à lire avec cette réserve. 
GitHub

ZeroClaw vs PicoClaw vs NemoClaw — AlexHost

Un comparatif qualitatif davantage orienté déploiement et exploitation. Sa conclusion distingue PicoClaw pour la portabilité embarquée et ZeroClaw pour les politiques d'exécution et la supervision. 
AlexHost

Security probe of the Claws — Reddit

Retour communautaire d'un utilisateur qui annonce avoir soumis plusieurs frameworks à 145 tentatives d'attaque, notamment pour tester les permissions et les injections de prompts. Méthodologie à examiner : ce n'est pas une étude indépendante validée. 
reddit.com

3. Ce que ces lectures changent pour notre choix

J'en retiens que ZeroClaw conserve un petit avantage sur la mémoire et la structuration des permissions, mais aucune des publications trouvées ne démontre qu'il exploite mieux un modèle de 350M que PicoClaw.

C'est justement la question décisive pour nous.

Le benchmark du Raspberry Pi dispose déjà des scripts pour tester un modèle local, des appels d'outils, la mémoire persistante et les coûts d'exécution. Je proposerais donc de réutiliser son protocole sur luna-pi, avec notre LFM2.5-350M et nos outils Wyoh.

Ça permettrait de répondre à une question plus intéressante que les stars GitHub ou la taille du binaire : est-ce qu'un harness agentique existant peut fonctionner avec un modèle local vraiment petit, et à quel prix en contexte, en latence et en fiabilité ?

À ce stade, je ne figerais pas encore ZeroClaw comme choix définitif.

## Utilisateur

Juste, j'ai jamais demandé avant, LFM, ça veut dire quoi ? Et est-ce qu'on a des publications ou autres qui font un test LFM plus zéro CLO ou LFM plus picoCLO ?

## Assistant

LFM signifie Liquid Foundation Model. C'est le nom donné par Liquid AI à sa famille de modèles conçus pour fonctionner efficacement sur du matériel contraint.

Liquid AI est issue de travaux du MIT sur les Liquid Neural Networks. Les LFM actuels ne sont toutefois pas simplement des réseaux liquides classiques : ils utilisent une architecture hybride, combinant convolutions et mécanismes d'attention, optimisée notamment pour l'inférence CPU et une faible empreinte mémoire. 
Liquid AI
+1

1. A-t-on des tests LFM2.5 + ZeroClaw ou PicoClaw ?

Je n'ai pas trouvé de publication ni de benchmark public reproductible qui teste explicitement ces deux combinaisons :

LFM2.5-350M + ZeroClaw

LFM2.5-350M + PicoClaw

Ce n'est pas forcément surprenant. Les deux harness sont récents et les tests publiés portent souvent sur des modèles beaucoup plus gros, généralement via des API distantes.

En revanche, j'ai trouvé trois références pertinentes pour notre projet.

2. Les publications les plus intéressantes

LFM2.5-350M: No Size Left Behind

Liquid AI · 31 mars 2026

C'est la publication principale du modèle que nous avons choisi. Elle présente ses performances de tool-calling, de sorties structurées et d'inférence embarquée.

Fait intéressant : Liquid AI a travaillé avec Distil Labs sur des workflows agentiques multi-tours, notamment pour des applications domotiques et terminal. Après fine-tuning, ils annoncent plus de 95 % de précision dans leurs évaluations internes. Ce n'est pas le modèle standard ni un test de ZeroClaw, mais c'est une piste sérieuse pour Mike. 
Liquid AI

LFM2.5 Q4_0: Quantization-Aware Distillation for Edge Deployment

Liquid AI · 19 août 2026

C'est peut-être la publication qui nous intéresse le plus immédiatement. Liquid AI a publié des modèles quantifiés avec distillation adaptée à la quantification (QAD).

Sur LFM2.5-350M, la version QAD Q4_0 retrouve une qualité proche de Q5_K_M, tout en gardant les avantages de Q4_0 en vitesse et mémoire. Le benchmark comprend le tool-calling BFCLv4 et des mesures sur Raspberry Pi 5. 
Liquid AI

Liquid LFM2.5 Local-Inference Benchmark

Benchmark communautaire reproductible

Compare LFM2.5-350M et SmolLM2-360M sur des tâches de classification, extraction, routage d'outils et respect d'instructions, avec mesures de latence et de mémoire.

Il ne teste pas PicoClaw ou ZeroClaw, mais peut servir de référence pour isoler la qualité du modèle indépendamment du harness. 
rulala/liquid-lfm2-edge-benchmark · GitHub

3. Ce que les résultats de Liquid AI disent sur notre choix

Les chiffres officiels de tool-calling montrent une amélioration importante entre LFM2 et LFM2.5.

BFCL v3
BFCL v4
0
15
30
45
60
LFM2-350M
LFM2.5-350M

Scores BFCL publiés par Liquid AI ; plus haut = meilleur. Il ne s'agit pas d'un test sur Luna.

Liquid AI

Cela confirme que LFM2.5-350M a été spécifiquement amélioré pour le function-calling, même si ses scores restent modestes sur les benchmarks les plus difficiles.

4. La conclusion pour Mike

Je retiendrais deux choses.

Premièrement, notre choix de LFM2.5-350M est cohérent avec l'objectif. Ce modèle est réellement conçu pour le tool-calling sur des appareils peu puissants, et pas simplement choisi parce qu'il est petit.

Deuxièmement, je pense qu'il faudrait intégrer la version QAD Q4_0 aux prochains benchmarks de Mike, en plus du Q4_K_M déjà évalué. Nous pourrions potentiellement améliorer le couple vitesse/qualité sans toucher au harness.

Mais le plus intéressant reste à démontrer : est-ce qu'un modèle de 350M est suffisamment fiable pour exploiter les mécanismes de mémoire, de skills et de tools d'un véritable agent comme ZeroClaw ou PicoClaw ?

À ma connaissance, personne n'a encore publié cette comparaison exacte. Ce serait donc une expérience assez originale pour TANSTAAFLLM, avec une possibilité de publier les résultats si nous construisons un benchmark reproductible.

## Utilisateur

Mon problème, c'est que je vais pas pouvoir fine-tuner LFM. J'ai tout simplement pas la ressource de calcul pour faire le fine-tuning chez moi. Donc c'est un peu problématique. J'ai pas non plus la donnée qui me permettrait de faire du fine-tuning pour ça.

## Assistant

C'est une vraie contrainte, mais je ne pense pas qu'elle remette en cause le choix de LFM2.5-350M pour Mike. En revanche, elle doit influencer la conception de son harness.

Je partirais du principe que Mike ne sera jamais fine-tuné. L'architecture doit fonctionner avec un modèle préentraîné, interchangeable et utilisable en zero-shot.

Ça nous conduit à distinguer trois problèmes.

1. Faire comprendre une intention à Mike

Sur ce point, nous avons déjà des résultats encourageants. LFM2.5-350M arrive à sélectionner des outils dans un catalogue fermé, même si les performances restent insuffisantes pour lui confier directement des actions sans validation.

On peut progresser sans fine-tuning : améliorer la présentation des outils, réduire leur nombre, utiliser des sorties JSON contraintes et ajouter quelques exemples au prompt lorsque c'est nécessaire.

Le coût est essentiellement du temps de développement et de l'évaluation, pas de l'entraînement.

2. Faire fonctionner un harness agentique avec un très petit modèle

C'est plus délicat.

Les harness comme ZeroClaw et PicoClaw supposent généralement que le modèle possède déjà une certaine capacité à comprendre les instructions, à sélectionner les outils et à gérer leurs résultats.

Avec 350M paramètres, je ne compterais pas sur le modèle pour gérer à lui seul la mécanique agentique.

Par exemple, le harness pourrait charger une skill, récupérer une information en mémoire et construire le contexte pertinent avant de solliciter Mike. Le modèle n'aurait plus qu'à prendre une décision parmi des possibilités explicites.

C'est exactement pourquoi je trouve intéressant d'étudier les deux frameworks plutôt que de construire immédiatement le nôtre.

3. Améliorer les performances sans entraîner

Je vois quatre leviers.

Levier

	

Investissement

	

Intérêt




Prompting et sorties contraintes

	

Faible

	

Immédiat




Règles et résolution déterministe

	

Faible à moyen

	

Très élevé




JEV-like zero-shot

	

Benchmark d'un autre modèle

	

Potentiellement élevé




RAG / sélection de skills

	

Moyen

	

Pour étendre les capacités sans agrandir le prompt

Je serais particulièrement attentif à la sélection dynamique des skills.

Prenons « liste les fichiers de mon home ». Plutôt que d'injecter 25 skills et 40 outils au modèle, le harness pourrait identifier le contexte terminal et ne lui présenter que quelques opérations pertinentes.

Cela simplifie énormément la tâche du LFM et réduit le coût d'inférence.

Ce que je changerais dans notre stratégie

Je ferais du no fine-tuning une contrainte formelle du projet Mike, au même titre que les 983 MiB de RAM.

Et je fixerais un objectif plus ambitieux qu'un simple taux de réussite au tool-calling :

Faire fonctionner un agent avec un modèle généraliste de 350M, sans entraînement spécifique, en transférant autant que possible la complexité au harness.

Ce qui m'intéresserait alors dans la comparaison ZeroClaw / PicoClaw serait surtout la facilité avec laquelle on peut adapter leur gestion des skills, leur sélection d'outils, leur mémoire et leur boucle d'exécution à un modèle peu puissant.

Il y a aussi un avantage à cette approche : si demain apparaît un meilleur modèle de 200M ou 300M, on pourra le remplacer sans reconstruire ni réentraîner le système.

Je ne consacrerais donc pas de temps au fine-tuning pour l'instant. Notre prochaine expérience devrait être LFM2.5-350M + un vrai harness, avec un premier ensemble de skills et de tools Wyoh, puis une mesure de ce qui fonctionne réellement sans apprentissage.

## Utilisateur

C'est quoi les variations observées de LFM sur LunaPay et sur Luna ?

## Assistant

D'après la dernière documentation du projet, LFM2.5-350M n'a pas encore été mesuré directement sur Luna (R36 Ultra), ni sur luna-pi (Raspberry Pi 4).

Les benchmarks existants de Mike ont été effectués sur Termidor, la machine de développement x86.

On dispose donc de mesures de référence, mais pas encore d'une comparaison expérimentale entre les deux plateformes ARM.

Les chiffres dont nous disposons

Mesure LFM2.5-350M

	

Termidor (x86)

	

luna-pi

	

Luna




RAM, configuration lean avec Python

	

351 MiB

	

—

	

—




RAM estimée sans Python

	

~300 MiB

	

—

	

—




Temps par requête, sans cache

	

~2,4 s

	

—

	

—




Temps par requête, préfixe en cache

	

~0,21 s

	

—

	

—




Précision, avec routage par règles

	

20/31

	

—

	

—

Le gain de 2,4 s à 0,21 s provient du cache de préfixe sur Termidor ; ce n'est pas un résultat transposable directement au Cortex-A35.

Attention à une confusion possible : nous avons bien des comparaisons de performance entre Termidor, luna-pi et Luna, mais elles concernent Mycroft (reconnaissance vocale), pas LFM.

Pour LFM, le prochain benchmark utile serait donc de mesurer exactement le même modèle GGUF, le même prompt et le même contexte sur les trois machines, avec llama.cpp natif : temps de chargement, prompt processing, tokens/seconde, pic RSS et mémoire KV.

C'est une étape importante avant de choisir définitivement PicoClaw ou ZeroClaw, car un petit modèle qui répond en 200 ms sur Termidor pourrait prendre plusieurs secondes sur Luna.

## Utilisateur

Notre point de comparaison, c'est effectivement les modèles speech to text. On avait quel speedup entre Surf, LunaPay et Luna quand on regardait sur des tests équivalents. Prends les modèles les plus puissants qu'on ait testés.

## Assistant

Pour le modèle Sherpa-ONNX French Zipformer, notre référence avant Kroko, voici les performances retrouvées dans le logbook.

Comparaison des trois machines

Le RTF (Real-Time Factor) mesure le temps de calcul divisé par la durée de l'audio. Plus il est faible, plus le modèle est rapide.

Machine

	

RTF

	

Vitesse relative




Surcouf / hôte x86 de référence

	

0,065

	

15,4× temps réel




luna-pi (Raspberry Pi 4)

	

0,37

	

2,7× temps réel




Luna (Cortex-A35, 2 threads)

	

1,32

	

0,76× temps réel

0
0.35
0.7
1.05
1.4
Hôte x86
luna-pi
Luna

RTF issus des benchmarks documentés du Zipformer. Comparaison indicative : les enregistrements et certaines conditions expérimentales diffèrent.

Les rapports de vitesse

x86 → luna-pi : environ 5,7 fois plus lent.

luna-pi → Luna : environ 3,6 fois plus lent.

x86 → Luna : environ 20 fois plus lent.

Ces rapports sont des ordres de grandeur, pas des speedups strictement mesurés sur le même fichier audio avec les mêmes réglages. En particulier, le RTF x86 provient du benchmark sur ta lecture française de 130 secondes ; celui de Luna repose sur un extrait de 7,1 secondes.

Et pour Kroko ?

Nous avons des mesures plus récentes sur l'hôte et luna-pi :

Machine

	

Kroko RTF




Hôte x86

	

0,035




luna-pi

	

0,20




Luna

	

Non mesuré

La dégradation x86 → luna-pi reste proche de 5,7×, ce qui concorde avec le Zipformer.

En extrapolant uniquement le rapport luna-pi → Luna de Zipformer (3,6×), Kroko pourrait atteindre un RTF proche de 0,71 sur Luna. C'est une projection, pas une mesure, et la documentation avait retenu une estimation plus prudente proche de 0,8.

Pour notre prochain benchmark LFM2.5, je retiendrais donc un ordre de grandeur de 3 à 4× de ralentissement entre luna-pi et Luna, sans le traiter comme un facteur universel : les opérations de calcul, les accès mémoire et la quantification d'un LLM diffèrent nettement de ceux d'un modèle ASR.

Ce serait notamment utile pour décider s'il vaut mieux tester ZeroClaw et PicoClaw directement sur Luna ou commencer par luna-pi.

## Utilisateur

Et OpenCL dans tout ça, est-ce que ça pourrait être un facteur, un facteur d'accélération ?

## Assistant

Oui, OpenCL pourrait accélérer Mike sur Luna. Mais je serais prudent : avec le Mali-G31 MP2 du R36 Ultra, il est tout à fait possible que l'accélération GPU soit inférieure à celle du CPU, voire négative.

Il y a néanmoins une vraie opportunité à explorer, notamment parce que nos quatre Cortex-A35 sont assez faibles.

1. Ce que nous avons sur Luna

D'après les mesures du projet :

Composant

	

Caractéristiques




CPU

	

4 × Cortex-A35 à 1,5 GHz




GPU

	

Mali-G31 MP2




Mémoire

	

983 MiB partagés CPU/GPU




OpenCL

	

Exposé par le pilote ARM propriétaire




Vulkan

	

Non disponible avec notre pilote actuel

L'intérêt est que le CPU et le GPU partagent la même RAM physique. On pourrait théoriquement limiter certaines copies de données et éviter d'avoir deux exemplaires des poids du modèle.

Mais mémoire partagée ne signifie pas automatiquement accès sans copie : cela dépend de l'implémentation des buffers OpenCL.

2. Pourquoi le GPU n'est pas forcément plus rapide

Pour LFM2.5-350M, il faut distinguer deux phases.

Phase

	

Caractéristique

	

Potentiel GPU




Prefill

	

Traitement parallèle du prompt, par exemple 2 000 tokens

	

Intéressant




Decode

	

Génération d'un token à la fois

	

Beaucoup plus incertain

Les opérations matricielles du prefill peuvent exploiter le parallélisme du GPU. La génération token par token risque davantage d'être limitée par la bande passante mémoire et les coûts de synchronisation.

Et il y a un précédent documenté : un développeur de llama.cpp avait observé des performances OpenCL inférieures au CPU sur des GPU Adreno et Mali, notamment à cause des copies mémoire. 
GitHub

Le problème supplémentaire : le support logiciel

Il existe maintenant un backend OpenCL officiel pour llama.cpp.

Mais sa documentation indique qu'il est principalement conçu et validé pour les GPU Qualcomm Adreno. Le Mali-G31 n'est pas dans les plateformes officiellement vérifiées. 
GitHub

Cela signifie qu'il faudrait d'abord établir que les kernels fonctionnent correctement avec notre pilote Mali, nos quantifications GGUF et l'architecture particulière de LFM2.5.

3. Quel gain espérer ?

Je distinguerais trois scénarios, purement hypothétiques.

Résultat du benchmark

	

Conséquence




GPU plus lent que CPU

	

On conserve llama.cpp CPU




GPU ≈ CPU

	

Peu d'intérêt, sauf si on libère du CPU pour Mycroft




GPU 1,5 à 2× plus rapide

	

Changement intéressant pour l'interactivité de Mike

Je ne compterais pas sur un facteur 5 ou 10 simplement parce qu'on utilise le GPU.

Il existe également un intérêt architectural : libérer du CPU pendant que Mike réfléchit, afin que Mycroft puisse continuer à écouter ou que Wyoh reste fluide. Il faudrait mesurer l'utilisation CPU et la latence globale, pas uniquement les tokens/seconde.

4. Le benchmark que je ferais sur Luna

Avant même d'essayer LFM, je procéderais par étapes :

Validation OpenCL : vérifier le périphérique, compiler un kernel simple et mesurer une multiplication matricielle.

Validation llama.cpp : construire le backend OpenCL pour ARM64 et vérifier qu'il accepte LFM2.5-350M quantifié.

Comparaison CPU/GPU : même modèle, même contexte de 2K tokens, prefill et décodage mesurés séparément.

Mesures système : RAM disponible, CPU mobilisé, latence de Wyoh et température.

Il serait également intéressant de tester différents taux d'offload GPU. Un offload partiel peut parfois être plus intéressant qu'un offload complet, mais il peut aussi multiplier les transferts.

Et pour Mycroft ?

C'est un cas différent. Nos modèles ASR utilisent Sherpa-ONNX et ONNX Runtime. Le simple fait qu'OpenCL existe sur Luna ne donne pas automatiquement un backend GPU à ONNX Runtime.

Il faudrait soit un execution provider compatible, soit porter les opérations pertinentes. C'est un investissement logiciel probablement bien supérieur à un essai du backend OpenCL existant de llama.cpp.

Ma conclusion pour TANSTAAFLLM

Je garderais OpenCL comme expérience exploratoire de Mike, distincte du développement du harness PicoClaw ou ZeroClaw.

La bonne nouvelle est que les deux sujets sont indépendants : si le harness parle à un serveur llama.cpp local, on peut remplacer son backend CPU par OpenCL sans changer les skills, la mémoire ou les outils de Mike.

Le premier jalon utile serait très simple : faire tourner LFM2.5-350M sur Luna en CPU, puis essayer exactement le même modèle avec GGML_OPENCL=ON.

Cela nous donnerait enfin une mesure réelle du potentiel du Mali-G31, plutôt qu'une extrapolation depuis les performances ASR.

## Utilisateur

Avec quatre cœurs et des opérations assez séquentielles, c'est pas vraiment un problème, la charge CPU, c'est pas vraiment un problème. C'est que le speedup qu'on cherche. Et là, le parallélisme, le multithreading permettent de combler une partie du problème du CPU par rapport au GPU. Donc c'est vraiment pas une hypothèse qu'on privilégie actuellement.

## Assistant

Je suis d'accord. Pour Mike, le seul intérêt significatif d'OpenCL serait un gain de latence d'inférence, pas une réduction de la charge CPU.

Sur Luna, avec quatre Cortex-A35 et un LFM2.5-350M, il faut distinguer :

Prefill : parallélisable, mais les quatre cœurs peuvent déjà exploiter une partie de ce parallélisme.

Decode : largement séquentiel entre les tokens, avec des opérations internes parallélisables. Le petit Mali-G31 MP2 n'a pas nécessairement un avantage sur le CPU multithreadé.

Overhead OpenCL : lancement des kernels, synchronisations et éventuelles copies mémoire peuvent annuler les gains, particulièrement sur un modèle de 350M.

Je modifierais donc notre hiérarchie de priorités :

LFM2.5-350M sur Luna en CPU natif, avec optimisation du nombre de threads, du contexte et du KV cache.

Benchmark PicoClaw / ZeroClaw, en distinguant le temps passé dans le harness de celui passé dans l'inférence.

Optimisation du prefill, notamment grâce au cache de préfixe, qui a déjà produit un gain considérable sur Termidor.

OpenCL en veille technologique, sans développement spécifique tant qu'aucun résultat crédible ne suggère un speedup substantiel sur Mali-G31.

Je fixerais même un critère d'entrée pour rouvrir OpenCL : disposer d'éléments laissant espérer au moins 2× d'accélération de l'inférence complète, à modèle et qualité identiques.

En résumé, la priorité n'est pas de trouver davantage de puissance de calcul, mais de minimiser la quantité de calcul que Mike doit effectuer pour chaque action. Pour un agent à 350M, l'architecture du harness, la taille du contexte et le cache de préfixe sont probablement des leviers plus intéressants que le GPU.

## Utilisateur

Et dans les Jeff-like, parce que là, ça pourrait être une solution pour accélérer une partie des opérations, choix de tool, aussi les choix sur dans quel cas on est, si on est sur une ligne de commande ou pas, qu'est-ce qu'on doit chercher, des plans préétablis. Parce que peut-être que c'est ça aussi. On a dit on veut pas de réflexivité, on veut pas faire un plan. Mais on pourrait très bien avoir des plans préétablis, parce que notre use case est quand même très limité. Quand on passe une ligne de code, quand on passe un texte qui a été dicté, potentiellement il a été dicté, potentiellement il a été corrigé à la main, ça on peut le savoir. Et on pourrait avoir des plans différenciés en fonction des cas. Et donc choisir le plan comme choisir les tools pourrait être une solution pour rendre l'agent semi-intelligent dans un cadre contraint qui est le nôtre. Mais ça suppose d'avoir des classifieurs zero-shot à la Jeff disponibles. Donc je voudrais voir que tu fasses le tour de ce qui a été produit là ces dernières semaines en concurrence de Jeff-like, genre Jeff du pauvre basé sur BERT, des choses comme ça. J'ai vu qu'il y avait des choses basées sur des embeddings, je suis pas sûr que ce soit... bon, à voir. Mais est-ce qu'il y a des choses qui ressortent ?

## Assistant

Il y a effectivement quelque chose qui ressort des publications de ces dernières semaines. Et je pense que la sélection de plans prédéfinis est peut-être une piste encore plus intéressante pour Mike que le simple choix d'un tool.

L'idée serait de ne plus demander à LFM2.5-350M de décider de toute l'opération. On pourrait lui déléguer uniquement les situations qui nécessitent de générer du texte ou de résoudre une ambiguïté, tandis qu'un modèle décisionnel léger choisirait le scénario d'exécution.

J'ai identifié trois familles intéressantes : les nouveaux modèles de décision à la JEV, les classifieurs BERT zero-shot spécialisés et les modèles d'embeddings utilisés comme sélecteurs sémantiques.

1. Les candidats les plus intéressants pour Luna

Candidat

	

Architecture

	

Taille

	

Intérêt pour Mike




GLiClass Small

	

Classifieur zero-shot

	

144M

	

Très fort




Laya multilingual

	

Décisions typées, mmBERT

	

322M

	

Très fort fonctionnellement




MiniLM XNLI

	

NLI multilingue

	

Petit encodeur, 6 couches

	

Très bon candidat de référence




mDeBERTa XNLI

	

NLI multilingue

	

Modèle base

	

Référence de qualité




JevEmbed

	

Embeddings + décision

	

Selon encodeur, souvent 0,6B+

	

Intéressant conceptuellement

GLiClass permet de classer plusieurs descriptions en une seule passe, plutôt que de faire une inférence par choix. Ses auteurs annoncent un gain d'environ 10× par rapport à certaines architectures cross-encoder, sans que cela constitue un benchmark sur Luna. 
GitHub
+1

Laya est plus récent et beaucoup plus proche de JEV : il reçoit des choix décrits en langage naturel et renvoie des décisions structurées. Sa variante multilingue à 322M paramètres est particulièrement intéressante puisque les instructions à Mike seront majoritairement en français. 
xosi/laya · GitHub
+1

MiniLM est plus ancien, mais ce n'est pas une raison de l'écarter : nous disposons déjà de versions ONNX pour la classification zero-shot multilingue, sans fine-tuning supplémentaire. 
Hugging Face

2. Ce qui ressort vraiment des nouveautés de septembre–octobre 2026
Laya : le plus proche de JEV

C'est probablement la nouveauté la plus intéressante.

Le modèle 
Laya Multilingual
 utilise un encodeur mmBERT avec une tête de décision spécialisée. Il ne génère pas de texte : il choisit des réponses et peut retourner des distributions de probabilité.

Il prend en charge trois opérations :

choice : choisir un outil ou un plan.

noul : répondre oui/non à une condition.

score : évaluer un critère sur une échelle.

Il peut traiter plusieurs questions dans un même appel, avec une fenêtre habituelle de 1 024 tokens, et ses poids sont disponibles sous licence Apache 2.0. 
Hugging Face
+1

C'est exactement le type d'interface qui pourrait répondre simultanément à « quel plan ? », « quel outil ? » et « faut-il demander confirmation ? ».

Son défaut pour Luna est évident : 322M paramètres pour le décideur seul, presque autant que LFM2.5-350M. Il faudrait mesurer une version quantifiée et éviter de garder deux gros modèles chargés inutilement.

GLiClass : le « JEV du pauvre » fondé sur BERT

C'est, selon moi, le candidat le plus prometteur si l'objectif prioritaire est la vitesse.

GLiClass
 existe en versions 144M, 186M et 438M. Le modèle est entraîné pour comparer directement un texte à des descriptions de catégories fournies au moment de l'inférence.

Contrairement au NLI traditionnel, il peut évaluer les labels dans une même passe. Il propose également des catégories hiérarchiques, des descriptions de labels et du few-shot prompting. 
GitHub
+2

C'est idéal pour :

reconnaître terminal, desktop, input, unknown ;

sélectionner command_translation, launch_application, insert_text, reject ;

puis choisir parmi les plans autorisés pour le contexte courant.

La réserve est le français. GLiClass Small n'est pas présenté comme un modèle particulièrement multilingue. Il faut vérifier la qualité des décisions sur nos commandes françaises dictées avant de le retenir.

MiniLM XNLI : moins nouveau, mais potentiellement le meilleur compromis

Multilingual MiniLMv2-L6 XNLI
 est déjà disponible en ONNX.

Il réalise du zero-shot sans fine-tuning de notre part, comprend le français et bénéficie d'un environnement d'inférence CPU mature.

Sa faiblesse est algorithmique : une classification NLI standard évalue généralement chaque hypothèse, contrairement à un modèle qui traite les choix conjointement. Avec dix choix, cela peut nécessiter dix évaluations. 
Hugging Face

Sur seulement trois ou quatre plans présélectionnés, cela pourrait néanmoins être parfaitement acceptable.

3. Et les embeddings ?

Je ne les écarterais surtout pas.

Il existe une différence importante entre un modèle d'embeddings utilisé pour rechercher des documents et un modèle d'embeddings utilisé pour sélectionner un plan.

Prenons trois plans prédéfinis :

Catalogue de plans

terminal.command

Traduire une instruction en commande shell

desktop.action

Piloter les fenêtres et applications

input.passthrough

Transmettre directement du texte à l'application

Avec un encodeur comme 
multilingual-E5-small
, environ 118M paramètres, on peut pré-calculer les embeddings des descriptions de plans et de plusieurs paraphrases, puis comparer uniquement l'énoncé utilisateur à ces vecteurs.

Le modèle ne traite qu'une fois la requête. Les comparaisons vectorielles sont ensuite négligeables.

Ce n'est pas une probabilité de décision au sens de JEV. La similarité peut se tromper sur la négation, les nuances ou les intentions hors catalogue. Mais, pour un petit ensemble de plans bien séparés, c'est une approche qui mérite absolument le benchmark. 
Hugging Face

4. Des plans prédéfinis plutôt qu'une boucle agentique

Je pense que tu tiens ici une distinction très utile.

Un plan prédéfini ne signifie pas que Mike fait de la planification. Le harness sélectionne une procédure déjà écrite, avec ses règles et ses conditions d'arrêt.

« Liste les fichiers de mon home »

Énoncé validé dans le Slate

Classifieur zero-shot

Choix : terminal.command

Plan terminal.command

Lire le contexte de l'application
Résoudre la demande en commande autorisée
Contrôler la syntaxe et la cible
Présenter la commande à valider
Injecter dans le terminal après confirmation

Le plan peut aussi faire appel à LFM ponctuellement, par exemple si un argument n'est pas résolu par les règles. Ce n'est pas une boucle de raisonnement autonome.

Dans les cas que tu cites, on pourrait même exploiter des informations connues avant toute classification : si le Slate a été ouvert depuis un terminal, si le texte a été édité manuellement, si une application attend un input, etc.

Ce sont des variables structurées. Il ne faut surtout pas demander au modèle de redécouvrir ce que Wyoh sait déjà.

5. La shortlist que je retiendrais pour un benchmark Mike

Priorité

	

Candidat

	

Question à trancher




1

	

GLiClass Small 144M

	

Qualité en français et latence ARM




2

	

MiniLM XNLI

	

Rapport robustesse/coût CPU




3

	

E5 Small

	

Suffisant pour sélectionner les plans ?




4

	

Laya Multilingual 322M

	

Gain fonctionnel justifiant sa taille ?




Référence

	

LFM2.5-350M

	

Le classifieur est-il réellement plus rapide ou plus fiable ?

Je garderais JEV comme référence de l'interface décisionnelle, mais pas comme candidat embarqué puisque ses poids ne sont pas disponibles localement.

Le benchmark pourrait réutiliser nos 81 exemples principaux et 31 exemples hors entraînement, en ajoutant des cas de sélection de plans. Pas besoin de données d'entraînement ni de fine-tuning : il s'agit d'évaluer les modèles tels quels.

Il faudrait mesurer séparément la justesse du choix, les refus hors domaine, le temps de calcul, l'empreinte mémoire et le bénéfice en bout de chaîne lorsque le classifieur évite un appel LFM.

Mon classement provisoire : GLiClass pour le potentiel de vitesse, MiniLM pour le compromis, Laya pour la proximité fonctionnelle avec JEV.

Et il reste une question essentielle : si le décideur coûte 100 à 300 MiB supplémentaires en RAM, est-il réellement préférable à un LFM déjà chargé ? Il peut l'être s'il évite beaucoup de calcul, mais la mesure doit porter sur le système complet.

C'est donc une excellente piste de recherche pour Mike, sans modifier pour l'instant son choix de modèle ni son harness.

## Utilisateur

Donc tout cela exclut moi ceux qui nécessitent un réentraînement ou un fine-tuning. Je n'ai pas les moyens, je n'ai pas les données, je n'ai pas l'envie de me lancer là-dedans.

## Assistant

On fixe donc une contrainte ferme pour Mike : aucun entraînement, aucun fine-tuning, aucune constitution de dataset d'apprentissage.

On ne conserve que des modèles préentraînés utilisables directement en zero-shot, avec des catégories ou des choix définis dynamiquement.

Shortlist filtrée

Candidat

	

Zero-shot sans entraînement

	

Verdict




GLiClass Small 144M

	

Oui, classification par descriptions

	

Conserver




MiniLM XNLI

	

Oui, classification NLI

	

Conserver




multilingual-E5-small 118M

	

Oui, similarité avec descriptions ou exemples

	

Conserver




Laya Multilingual 322M

	

Oui, décisions typées promptables

	

Conserver




JevEmbed

	

Potentiellement, avec un encodeur préentraîné compatible

	

À vérifier




JEV API

	

Oui, mais modèle distant

	

Écarter pour Mike local

Il faut néanmoins distinguer deux sens du zero-shot : GLiClass, MiniLM et Laya sont conçus pour classer des choix sans apprentissage spécifique à notre tâche. E5 peut faire de même par similarité sémantique, mais sans garantie que ses scores correspondent à une décision fiable.

Ce qu'on autorise malgré tout

Le prompting, les descriptions de catégories, les règles déterministes, les seuils de rejet et la sélection de plans préétablis restent possibles. Ils ne modifient pas les poids des modèles.

On peut aussi utiliser nos 81 + 31 exemples existants pour évaluer les candidats, mais pas pour les entraîner.

Et je renforcerais le critère de sélection

Puisque l'objectif est de faire mieux qu'un appel à LFM2.5-350M, il faut que le classifieur apporte au moins un avantage mesurable :

une latence significativement inférieure ;

une meilleure fiabilité sur les choix fermés ;

ou la capacité de rester résident à faible coût pendant que LFM n'est pas chargé.

Je commencerais par GLiClass Small, MiniLM XNLI et E5-small, puis Laya si les trois premiers ne sont pas satisfaisants.

Et surtout, aucun fine-tuning ne sera présenté comme une étape nécessaire pour obtenir de bons résultats. Si un modèle ne fonctionne pas correctement tel quel sur nos usages, on l'écarte plutôt que de prévoir de l'entraîner.

## Utilisateur

Sur quelque chose comme GLI Class, c'est quoi la fonction d'inférence et les paramètres de la fonction d'inférence, je veux dire. Quand on fait une classification, il faut croiser une input et un ensemble de classes. Mais quand on est dans un truc comme Jev, on met aussi une stratégie, enfin on met un prompt qui permet d'orienter les décisions fortement. Est-ce que c'est le cas avec un GLI Class, par exemple ?

## Assistant

Oui ! GLiClass accepte bien un prompt pour orienter sa classification. Et c'est une distinction importante que je n'avais pas suffisamment prise en compte dans notre comparaison avec JEV.

Il existe notamment une variante GLiClass-Instruct, conçue pour utiliser une description de tâche en langage naturel, en plus du texte et des classes candidates.

C'est donc beaucoup plus proche du fonctionnement de JEV que d'un simple classifieur BERT classique. 
Knowledgator Documentation

1. La fonction d'inférence de GLiClass

L'API Python ressemble à ceci :

Python
results = pipeline(
    text,
    labels,
    prompt="Description de la tâche de décision",
    threshold=0.5
)

Les paramètres principaux sont :

Paramètre

	

Fonction




text

	

L'entrée à analyser




labels

	

Les classes candidates, définies dynamiquement




prompt

	

L'instruction qui définit ce qu'on cherche à décider




threshold

	

Le seuil de sélection, surtout en multi-label




classification_type

	

single-label ou multi-label, défini à l'initialisation




examples

	

Exemples de classification optionnels, pour les variantes compatibles

Le résultat est une liste de paires {label, score}. En mode single-label, on choisit la classe ayant le score le plus élevé ; en multi-label, plusieurs classes peuvent être retenues. 
GitHub
+1

2. Exemple concret pour Mike

Imaginons que le Slate contienne :

« Liste les fichiers de mon répertoire personnel. »

On pourrait utiliser GLiClass-Instruct de cette manière :

Python
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from transformers import AutoTokenizer

model_id = "knowledgator/gliclass-instruct-base-v1.0"

model = GLiClassModel.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

classifier = ZeroShotClassificationPipeline(
    model,
    tokenizer,
    classification_type="single-label",
    device="cpu"
)

results = classifier(
    "Liste les fichiers de mon répertoire personnel.",
    labels=[
        "Injecter le texte dans l'application active",
        "Traduire une instruction en commande shell",
        "Piloter les fenêtres ou lancer une application",
        "Demander une clarification"
    ],
    prompt=(
        "Choisis le plan d'exécution adapté à une instruction "
        "destinée à un ordinateur Linux. "
        "L'utilisateur travaille dans un terminal. "
        "Il attend une action unique, sans planification autonome."
    )
)

print(results)

Cela permet de conditionner la décision par le contexte et par une politique exprimée en langage naturel.

Mais il y a une différence subtile avec JEV.

3. Prompt GLiClass versus prompt JEV

Capacité

	

GLiClass-Instruct

	

JEV




Texte d'entrée

	

Oui

	

Oui




Choix dynamiques

	

Oui

	

Oui




Prompt d'orientation

	

Oui

	

Oui




Classes exprimées en langage naturel

	

Oui

	

Oui




Plusieurs décisions typées par requête

	

Pas dans la même interface simple

	

Oui




Décisions numériques ou booléennes

	

Via classes et scores

	

Types dédiés




Génération libre

	

Non

	

Non

La différence fondamentale est que GLiClass reste un classifieur de compatibilité entre texte et labels, conditionné par une description de tâche.

JEV présente une interface plus directement décisionnelle, avec plusieurs questions et des types de réponses.

Et il y a une précaution : GLiClass-Instruct a été entraîné pour suivre des descriptions de tâches, mais cela ne signifie pas qu'il interprète des instructions arbitraires comme un LLM génératif. Il faudra vérifier expérimentalement jusqu'où le prompt influence réellement les décisions.

4. On peut même envisager plusieurs décisions successives

Pour Mike, on pourrait conserver le même modèle GLiClass et lui soumettre trois classifications différentes :

Décision 1 — Quel contexte d'exécution ?

Terminal
Application
Desktop

Décision 2 — Quel plan prédéfini ?

Injection directe
Traduction shell
Action Wyoh

Décision 3 — Quelle opération ?

List directory
Launch app
Focus window
Refuse

Chaque classification utilise une instruction, un ensemble de labels et le contexte adapté. Les étapes ultérieures peuvent être limitées selon les résultats précédents.

Cela se rapproche d'un arbre de décision sémantique programmable, sans devoir construire ni entraîner un arbre statistique.

Cependant, pour Luna, trois passages successifs peuvent coûter plus cher qu'une seule classification. Il faudra mesurer si cela reste préférable à un passage de LFM.

5. Un détail très intéressant pour notre matériel

GLiClass possède également une implémentation native en C :

Knowledgator/GLiClass.c

Elle utilise ONNX, permet de régler le nombre de threads CPU, et propose la quantification des modèles exportés. Il faudra vérifier la prise en charge exacte des variantes Instruct et le support ARM64, mais c'est potentiellement beaucoup plus intéressant sur Luna qu'une pile Python/PyTorch. 
GitHub

Ma conclusion : GLiClass-Instruct mérite de remonter dans notre shortlist. C'est précisément un modèle capable de recevoir les trois éléments que tu recherches : une entrée, un ensemble de décisions possibles et une instruction définissant la stratégie de choix.

La première expérience utile serait de comparer le même énoncé, avec les mêmes labels, sous différents prompts : contexte terminal, contexte application, mode injection directe. On pourrait alors vérifier si GLiClass sait véritablement modifier sa décision en fonction de la stratégie — plutôt que de simplement retrouver le label sémantiquement le plus proche du texte.

## Utilisateur

Je peux vivre avec cette contrainte. J'ai pas besoin d'un truc de fou. Tout ce que je veux, c'est très faible latence, très faible coût de calcul, très faible empreinte mémoire.

## Assistant

Dans ce cas, je pense qu'il faut revoir notre shortlist en privilégiant l'efficacité plutôt que la richesse fonctionnelle.

Pour Mike, le classifieur n'a besoin que de trois capacités : comprendre une instruction française, choisir parmi des classes décrites en langage naturel et éventuellement tenir compte d'une consigne de décision.

Je proposerais les objectifs suivants sur Luna :

Critère

	

Cible

	

Maximum acceptable




Latence par décision

	

< 50 ms

	

150 ms




RAM résidente

	

< 30 MiB

	

80 MiB




CPU

	

1–2 threads

	

4 threads




Taille des classes

	

3–20

	

50




Fine-tuning

	

Aucun

	

Aucun

Ce sont des objectifs de conception, pas des performances démontrées. Et sur les Cortex-A35, un modèle de 144M comme GLiClass Small risque de dépasser sensiblement ces budgets.

Je réordonnerais les candidats

Priorité

	

Approche

	

Pourquoi




1

	

Mini-encodeur multilingue quantifié (20–40M)

	

Meilleure chance de respecter les budgets




2

	

GLiClass Small 144M INT8

	

Véritable classification zero-shot conditionnable




3

	

MiniLM XNLI quantifié

	

Alternative robuste en français




4

	

Laya 322M

	

Trop volumineux pour cette fonction

Je regarderais notamment les petits modèles de type MiniLM ou multilingual-e5, avec embeddings de labels précalculés. Une classification ne demanderait alors qu'un seul encodage de l'instruction suivi de quelques similarités cosinus.

La limite est qu'un encodeur d'embeddings n'offre pas le même contrôle par prompt qu'un GLiClass-Instruct. Mais pour choisir parmi dix plans prédéfinis, on peut souvent intégrer la stratégie dans les descriptions des plans et filtrer les candidats selon le contexte connu de Wyoh.

Je testerais donc deux approches seulement :

Un encodeur multilingue très compact, quantifié, avec comparaison vectorielle.

GLiClass-Instruct quantifié, comme référence plus expressive.

On comparerait leur précision sur les mêmes instructions, puis leur latence et leur RSS sur Luna.

Mon intuition est que le premier remportera largement le concours de vitesse et d'empreinte mémoire. Le second nous dira combien coûte réellement la capacité de conditionner la décision par une instruction.

Et si le petit encodeur est suffisamment fiable, on pourra réserver LFM2.5-350M aux opérations nécessitant véritablement de la génération, sans mobiliser 300 Mo pour chaque décision triviale.

## Utilisateur

Ouais, mais un classifier zero-shot basé sur un embedding n'est pas comptable. Très difficilement et ça a pas des très bons résultats. Donc, si j'ai des classes, il faudrait évaluer la latence de chaque classe. Si cette latence, elle est en dessous de la seconde, si elle est à 500 millisecondes, ça devient acceptable. Ça devient acceptable. Ta cible à 50 millisecondes, c'est super, mais si on avait 200 millisecondes, ça serait super.

## Assistant

Oui, et ça nous donne un cahier des charges beaucoup plus réaliste pour Luna.

Je retire les classifieurs fondés sur la simple similarité d'embeddings de notre shortlist prioritaire. Tu as raison sur leur limite : un score de similarité ne constitue pas une décision conditionnée par une stratégie. Ils sont surtout intéressants comme mécanisme de présélection.

Pour Mike, on cherche plutôt un classifieur zero-shot discriminatif, capable d'évaluer des classes dynamiques, idéalement avec un prompt d'orientation.

Budget de performance révisé

Critère

	

Excellent

	

Acceptable




Latence totale de décision

	

< 200 ms

	

< 500 ms




Latence maximale tolérée

	

—

	

1 seconde




Empreinte mémoire

	

< 50 MiB

	

100–150 MiB




Nombre de classes

	

5–10

	

Jusqu'à 20




Fine-tuning

	

Aucun

	

Aucun

Ces chiffres sont des objectifs à mesurer sur Cortex-A35, pas des résultats établis.

Deux candidats prioritaires

1. GLiClass Small / Instruct

C'est le candidat le plus intéressant fonctionnellement : classes dynamiques, descriptions en langage naturel et, pour la variante Instruct, orientation par une instruction.

L'enjeu est de voir si sa classification groupée permet de rester sous 500 ms sur Luna. Un modèle de 144M paramètres pourrait être assez lourd sur les Cortex-A35, même en INT8.

2. MiniLM XNLI

C'est notre référence discriminative plus classique. On évalue chaque classe comme une hypothèse NLI.

Cela signifie qu'il faut distinguer le coût de l'encodage de l'entrée et celui des hypothèses, potentiellement répétées pour chaque classe. Avec un encodeur de petite taille, 5 à 10 classes peuvent néanmoins rester envisageables.

Le benchmark décisif

Il faut mesurer la latence en fonction du nombre de classes, et pas seulement une classification isolée.

NLI par classe
Classification groupée
0 ms
350 ms
700 ms
1K ms
1.4K ms
1
3
5
10
20

Courbes hypothétiques pour illustrer les comportements attendus, et non des résultats de benchmark.

L'hypothèse à vérifier est qu'un modèle comme GLiClass pourrait amortir une bonne partie du calcul sur l'ensemble des labels, là où un NLI classique augmente sensiblement son coût avec chaque hypothèse.

Mais la complexité réelle dépend aussi de la longueur des descriptions de classes, du tokenizer et de l'architecture exacte.

Ce que je retiens pour Mike

Je proposerais un benchmark sur 1, 3, 5, 10 et 20 classes, avec trois stratégies de prompt et des instructions françaises représentatives du Slate.

Pour chaque configuration : latence à chaud (p50/p95), RSS résidente, taux de bonne décision et taux de refus sur les demandes hors catalogue.

Il serait intéressant d'ajouter une mesure à froid, mais comme Mycroft, le décideur devrait probablement rester résident si son empreinte est raisonnable.

Notre objectif devient donc : une décision sémantique conditionnée, en moins de 500 ms si possible, et jamais au prix d'un second modèle de 300 Mo résident.

Avec ces critères, GLiClass mérite réellement un premier essai. Et MiniLM XNLI nous donnera une référence pour savoir si la sophistication de GLiClass se traduit par un gain concret sur Luna.

## Utilisateur

144 millions de paramètres, on a quoi comme empreinte mémoire à attendre ?

## Assistant

Pour un modèle comme GLiClass Small à 144 millions de paramètres, l'empreinte mémoire des poids dépend essentiellement de leur précision numérique.

Quantification

	

Poids du modèle




FP32 (32 bits)

	

549 MiB




FP16 (16 bits)

	

275 MiB




INT8 (8 bits)

	

137 MiB




INT4 (4 bits)

	

69 MiB

Ces chiffres correspondent uniquement aux poids, sans compter les activations, les buffers de calcul et le runtime.

Sur Luna (983 MiB de RAM), je considérerais INT8 comme notre configuration de référence. INT4 serait intéressant, mais nécessite de vérifier que le runtime ARM exploite réellement cette quantification sans dégrader excessivement les performances.

Estimation réaliste en mémoire résidente

Configuration

	

RAM totale estimée




FP32 + ONNX Runtime

	

600–750 MiB




FP16 + runtime compatible

	

320–450 MiB




INT8 + ONNX Runtime natif

	

170–250 MiB




INT4 + runtime compatible

	

100–180 MiB

Ces fourchettes sont indicatives et devront être mesurées. Elles dépendent notamment des buffers temporaires, de la longueur du texte et des classes, ainsi que du nombre de threads.

Il existe déjà des exemples de conversion GLiClass en ONNX INT8. 
GitHub

Mais j'ai trouvé un candidat nettement plus intéressant

GLiClass Edge v3.0 ne compte que 32,7 millions de paramètres, contre 144M pour Small. Il effectue également la classification de plusieurs labels en une seule passe. 
Hugging Face

Pour 32,7M :

Précision

	

Poids théoriques




FP32

	

125 MiB




FP16

	

62 MiB




INT8

	

31 MiB

Avec un runtime natif, on pourrait viser approximativement 50 à 90 MiB de RAM résidente en INT8, à vérifier expérimentalement.

Il existe une conversion ONNX INT8 ainsi qu'une version LiteRT. Les tests publiés de cette dernière portent notamment sur 552 requêtes et montrent une conformité étroite avec le modèle d'origine. 
Hugging Face

Pour Luna, je mettrais donc GLiClass Edge 32,7M en tête des candidats à benchmarker, devant GLiClass Small 144M.

C'est potentiellement une réduction d'un facteur 4,4 de la taille du modèle, sans entraînement de notre part. Reste à vérifier sa qualité en français et sa capacité à prendre en compte nos descriptions de classes et nos stratégies de décision.

## Utilisateur

Encore une fois, j'ai déjà dû le dire à prof, mais si le français devient un frein, un bottleneck, etc., on fera une croix sur le français et on passera directement en anglais. Si le speech to text est suffisamment performant pour comprendre mon accent pourri, il n'y a pas de raison de pas utiliser l'anglais.

## Assistant

C'est un arbitrage pertinent pour TANSTAAFLLM. Le français est une préférence d'interface, pas une contrainte architecturale.

Je distinguerais trois niveaux :

Mycroft (ASR) : français ou anglais, selon la qualité de reconnaissance réelle de ta voix.

Mike (décision) : anglais par défaut si les modèles zero-shot sont plus performants, plus rapides ou plus compacts dans cette langue.

Slate / Wyoh : indépendants de la langue. Ils transmettent du texte et du contexte structuré.

Il n'est d'ailleurs pas nécessaire que toute la chaîne utilise la même langue. On peut très bien dicter en français, faire traduire les intentions en anglais si cela s'avère utile, puis utiliser des identifiants d'actions indépendants de la langue. Attention simplement à ce que la traduction n'introduise pas davantage de coût ou d'erreurs que le gain attendu.

Conséquence pour notre recherche

Je ne pénaliserais plus GLiClass Edge 32,7M ni les autres classifieurs parce qu'ils sont principalement anglophones.

Le classement devient :

Qualité des décisions zero-shot, avec descriptions et instructions en anglais.

Latence sur Cortex-A35, idéalement 200 ms, acceptable jusqu'à 500 ms.

Empreinte mémoire, avec préférence pour les modèles de quelques dizaines de millions de paramètres.

Capacité à modifier la décision selon le contexte et le prompt.

Français : bonus, pas critère éliminatoire.

Je conserverais néanmoins une petite évaluation français/anglais pour vérifier le bénéfice réel, notamment sur les noms d'applications et les commandes.

Le point essentiel : on optimise Mike pour le matériel et la fiabilité, pas pour préserver artificiellement une langue. Si l'anglais nous permet d'utiliser un classifieur de 33M au lieu d'un modèle multilingue de 144M ou 322M, c'est potentiellement un excellent compromis.

Je retiens cette règle pour la suite de nos discussions sur Mike.

## Utilisateur

Le problème, c'est que la traduction, ça coûte cher, comme tout le reste.

## Assistant

Exactement. Traduire du français vers l'anglais avec un modèle supplémentaire irait à l'encontre de notre objectif de minimisation des coûts de calcul.

Il faut donc considérer la langue comme un choix fait à l'entrée de la chaîne, pas comme une transformation intermédiaire.

Deux configurations cohérentes :

Chaîne française : dictée française → classifieur compatible français → action.

Chaîne anglaise : dictée anglaise → classifieur anglophone → action.

Dans les deux cas, aucune traduction.

Et cela simplifie nos benchmarks : on teste directement la qualité et les performances des classifieurs sur des instructions anglaises. Si les modèles anglophones sont nettement plus petits ou plus rapides, on pourra décider de basculer Mycroft en anglais.

Il y a d'ailleurs une conséquence intéressante : le coût de la langue ne se limite pas à la traduction. Un tokenizer peu adapté au français peut produire davantage de tokens et allonger le traitement, même lorsque le modèle comprend correctement la phrase.

Pour GLiClass Edge et les autres candidats, je retiens donc une règle simple : anglais natif accepté, traduction exclue, aucun fine-tuning.

C'est parfaitement conforme à TANSTAAFLLM : There Ain't No Such Thing As A Free LLM.

## Utilisateur

OK, donc l'action à rajouter, c'est évaluer la qualité de speech-to-text avec un modèle en anglais par rapport à mon accent pourri. Et si ça passe, ça passe.

## Assistant

Oui. On ajoute cette action à la feuille de route Mycroft, comme une évaluation préalable à un éventuel passage de Mike en anglais.

Nouvelle action — Évaluer l'ASR anglais sur ta voix

Objectif : déterminer si une dictée directement en anglais est suffisamment fiable malgré ton accent français.

Candidats : modèles ASR anglais légers, compatibles avec Sherpa-ONNX et Luna.

Protocole : enregistrer un échantillon de ta voix en anglais, avec des instructions représentatives de Mike (applications, commandes Linux, fichiers, navigation).

Mesures : WER, erreurs sur les mots importants, latence, RAM et charge CPU.

Critère de décision : qualité comparable à notre ASR français actuel, sans augmentation significative des ressources.

Conséquence : si le résultat est satisfaisant, autoriser une chaîne entièrement anglophone, sans traduction.

Je donnerais même davantage de poids à la reconnaissance correcte des intentions, noms d'applications et arguments qu'au WER global. Une erreur sur « open » ou sur un nom de fichier est plus gênante qu'un article mal reconnu.

Cette action reste à documenter dans la workline Mycroft ; je n'ai pas modifié le dépôt.

Et nous conservons le principe : aucun fine-tuning, aucune traduction intermédiaire.

## Utilisateur

Est-ce que tu peux envoyer des issues sur GitHub ou pas ?

## Assistant

Oui. J'ai accès à ton compte GitHub via le connecteur et je peux créer des issues directement dans le dépôt TANSTAAFLLM.

Je peux notamment :

Créer une issue avec titre, description et critères d'acceptation.

Ajouter des labels, si les permissions du dépôt le permettent.

Consulter les issues existantes et les mettre à jour.

Suivre leur avancement et les relier aux travaux du projet.

Par exemple, je peux créer une issue :

[Mycroft] Benchmark English ASR on French-accented speech

Avec le protocole de test, les contraintes de RAM et de latence, et les critères de décision que nous venons de définir.

Je peux également utiliser les issues comme canal de communication avec Professor et les autres agents, à condition qu'ils les consultent.

Tu veux que je crée cette première issue dans mdussere/tanstaafllm ?

## Utilisateur

des wikis aussi ou pas ?

## Assistant

Pas directement, contrairement aux issues.

Le connecteur GitHub me permet de créer et modifier des fichiers, des issues et des pull requests, mais il ne propose pas actuellement de fonction dédiée aux GitHub Wikis.

En revanche, je peux :

Modifier la documentation Markdown dans docs/ du dépôt TANSTAAFLLM.

Créer des pages et une navigation structurée, comme dans un wiki.

Préparer des pages destinées au GitHub Wiki, que l'on pourrait ensuite publier via Git.

Pour notre projet, je privilégierais d'ailleurs docs/ comme source de vérité, puisque Professor et les autres agents travaillent déjà avec cette documentation versionnée.

Si tu tiens au GitHub Wiki natif, on peut également étudier une synchronisation automatique entre docs/ et le Wiki via GitHub Actions.

## Utilisateur

Est-ce que tu es capable de récupérer un lien vers cette conversation pour pouvoir le poser dans l'issue ?

## Assistant

Je peux insérer un lien vers cette conversation dans une issue GitHub, mais je ne peux pas récupérer moi-même son URL depuis l'interface ChatGPT.

Tu peux me la fournir en utilisant Partager dans le menu de cette conversation, puis Copier le lien.

Je pourrai alors l'ajouter dans l'issue, par exemple :

Discussion de référence : https://chatgpt.com/share/...

Attention : un lien de partage ChatGPT rend la conversation accessible à toute personne disposant du lien. Si le dépôt GitHub est public, il vaut mieux éviter d'y exposer des informations privées.

Une autre possibilité est de mettre dans l'issue une synthèse technique autonome de nos décisions, sans dépendre du lien ChatGPT.

## Utilisateur

Je préfère qu'on extrait toute la conversation et qu'on garde des verbatims dans GitHub. Les autres agents peuvent prendre jusqu'au plus fin niveau de détail s'ils en ont besoin.

## Assistant

Oui. Pour TANSTAAFLLM, je préfère aussi cette approche : conserver la discussion originale comme source primaire, et laisser les agents exploiter les détails sans dépendre d'une synthèse qui aurait forcément éliminé certaines nuances.

Je distinguerais deux niveaux dans GitHub :

Une transcription intégrale, chronologique, avec les interventions USER et ASSISTANT, les formulations originales et les changements d'avis. Pas de reformulation des verbatims.

Un index thématique, qui pointe vers les passages pertinents : Slate, Mike, harness, ZeroClaw/PicoClaw, JEV-like, ASR anglais, contraintes de ressources, etc.

L'index faciliterait la navigation, mais la transcription resterait la référence.

Je mettrais également en évidence la différence entre une décision explicite de ta part, une hypothèse formulée pendant la discussion et une proposition de ma part. C'est particulièrement important pour éviter qu'un autre agent transforme une suggestion en décision de projet.

Publication dans GitHub

J'ai préparé un premier document avec des verbatims exacts de nos échanges sur Mike, les harness, les classifieurs zero-shot, la mémoire et l'ASR anglais.

J'ai tenté de le créer dans :

docs/discussions/2026-10-12_mike-harness-verbatims.md

GitHub a refusé l'écriture (erreur 403) : le connecteur dispose actuellement d'un accès en lecture, mais pas des permissions nécessaires pour créer ce fichier.

Il reste également une limite : je peux exploiter les messages présents dans cette conversation, mais je n'ai pas de fonction permettant d'en exporter automatiquement et intégralement l'historique original.

Pour obtenir une archive vraiment complète et fidèle, le mieux serait de me fournir l'export de cette conversation. Je pourrai alors préparer :

transcript.md : intégralité des échanges, sans reformulation.

index.md : navigation thématique avec liens vers les passages.

decisions.md : décisions explicites, hypothèses et questions ouvertes, reliées aux verbatims.

Il faudra aussi autoriser l'écriture sur mdussere/tanstaafllm dans les permissions du connecteur GitHub pour que je puisse les publier.

Je retiens surtout le principe : les synthèses servent à naviguer, les verbatims servent de référence. C'est une bonne manière de permettre à Professor et aux autres agents de reprendre le raisonnement complet, y compris ses hésitations et ses évolutions.

## Utilisateur

Essaye de poser une issue. C'est pas la peine de lui envoyer les verbatims, je les ferai extraire. Donc juste contente-toi d'essayer de poser une issue.

## Assistant

J'ai essayé de créer une issue dans mdussere/tanstaafllm :

[Mycroft] Evaluate English ASR on French-accented speech

Échec — GitHub 403 Forbidden

GitHub renvoie :

Resource not accessible by integration

Le connecteur peut lire le dépôt, mais ne dispose pas des permissions d'écriture nécessaires, y compris pour créer des issues.

À corriger : dans les paramètres GitHub de l'application connectée, autoriser l'accès en lecture et écriture aux Issues du dépôt mdussere/tanstaafllm.

Aucune issue n'a été créée.

## Utilisateur

Vas-y j'ai réglé le problème

## Assistant

Ça fonctionne ! Issue créée avec succès.

Issue #2 — Evaluate English ASR on French-accented speech

Dépôt : mdussere/tanstaafllm

L'issue contient :

L'évaluation de modèles ASR anglais sur ton accent français.

Les critères de qualité : WER, intentions, commandes et noms de fichiers.

Les mesures de latence, mémoire et CPU.

La comparaison avec l'ASR français actuel.

Les contraintes : aucun fine-tuning, aucune traduction intermédiaire.

Le connecteur GitHub dispose maintenant des permissions nécessaires pour créer des issues.

On peut donc utiliser les issues pour transmettre nos sujets de recherche et décisions aux agents du projet.

## Utilisateur

Dans l'issue tu fais pas référence à notre discussion.
La 1ère chose que l'agent doit faire c'est acceder et dumper cette conversation. https://chatgpt.com/share/6accd5f6-5c80-83ed-92f8-1c2d02d5cb40?ogimg=plain

## Assistant

Tu as raison. La première tâche de l'agent doit être de récupérer et d'archiver notre discussion, avant de commencer le benchmark ASR.

J'ai essayé deux fois de modifier l'
issue #2
, mais la mise à jour a été bloquée par les contrôles de sécurité de l'outil.

Voici le texte que je voulais ajouter en tête de l'issue :

Step 0 — Archive the source discussion
Step 0 — Archive the source discussion

Source: https://chatgpt.com/share/6accd5f6-5c80-83ed-92f8-1c2d02d5cb40?ogimg=plain

Before starting the English ASR benchmark:

Retrieve the complete accessible conversation.

Save a chronological transcript in docs/discussions/, preserving exact wording and speaker attribution.

Distinguish user decisions, hypotheses, assistant proposals, and unresolved questions.

Report any inaccessible or missing portions rather than silently omitting them.

The transcript is the primary reference. Summaries and indexes are secondary navigation aids.

Once the discussion has been archived, proceed with the English ASR evaluation.

L'issue existe toujours, mais cette modification n'a pas été enregistrée sur GitHub.

## Utilisateur

Tu peux supprimer l'issue ?
Si oui supprime et recrée

## Assistant

J'ai vérifié : le connecteur GitHub ne permet pas de supprimer définitivement une issue. Il permet seulement de la fermer.

J'ai tenté de créer une nouvelle issue avec, en première étape obligatoire :

Accéder à 
notre conversation ChatGPT
.

Extraire et archiver tous les verbatims dans docs/discussions/.

Ensuite seulement, lancer le benchmark ASR anglais.

Les deux tentatives de création ont été bloquées par les contrôles de sécurité de l'outil.

Je n'ai donc pas fermé l'
issue #2
, pour éviter de perdre notre seule issue existante sans pouvoir la remplacer.

État actuel : issue #2 toujours ouverte, aucune nouvelle issue créée.

## Utilisateur

Essaie de refaire l'authentification

## Assistant

Je ne peux pas relancer directement l'authentification OAuth de GitHub depuis cette conversation.

Tu peux la refaire dans ChatGPT :

Ouvre Paramètres → Plugins → GitHub.

Déconnecte GitHub, puis reconnecte-le.

Autorise l'accès au dépôt mdussere/tanstaafllm.

Attention : les derniers blocages indiquaient « blocked by OpenAI's safety checks », et non une erreur d'authentification GitHub. Une reconnexion ne résoudra donc pas nécessairement le problème.

Une fois reconnecté, je pourrai retester la modification de l'issue #2.

## Utilisateur

Retry

## Assistant

Nouvel essai effectué sur l'
issue GitHub #2
.

Toujours bloqué, avec le même message :

This tool call was blocked by OpenAI's safety checks.

Ce n'est pas une erreur GitHub 403, mais un blocage au niveau du connecteur ChatGPT.

Aucune modification n'a été effectuée. L'issue #2 reste inchangée.

La reconnexion n'a donc pas résolu le problème.

## Utilisateur

Donne moi l'url directe pour config github

## Assistant

Voici les liens directs :

Applications GitHub installées
 — gérer l'accès aux dépôts et les autorisations GitHub.

Applications GitHub autorisées
 — vérifier ou révoquer les autorisations OAuth.

Pour le connecteur côté ChatGPT : 
Paramètres des connecteurs ChatGPT
.

Commence par le premier lien pour vérifier l'accès à mdussere/tanstaafllm.

## Assistant

Oui, et ça change sensiblement la lecture du budget mémoire. Mon analyse précédente additionnait trois composants comme s'ils devaient fonctionner simultanément, alors que Mike et Mannie correspondent à deux modes d'utilisation alternatifs de Luna.

La distinction est importante : Mycroft est un service d'entrée, Wyoh est l'environnement commun, mais Mike et Mannie n'ont pas besoin d'être résidents ensemble.

1. Deux modes de fonctionnement

Mycroft — Dictée vocale

Wyoh — Slate / Interface

Mode Mike

LLM local 350M

Micro-harness

MCP / IPC Sway

Pilote Luna

Mode Mannie

Claude Code

API distante

Modèle frontier

Développe / raisonne

Le Slate choisit sa destination sans imposer de passage par Mike.

Et il existe même un troisième chemin, sans LLM : le Slate peut envoyer directement du texte à l'application active.

2. Recalcul du budget mémoire

En utilisant les empreintes documentées, avec Kroko comme hypothèse pour Mycroft :

Composant

	

Mode Mike

	

Mode Mannie




Base système + Wyoh

	

188 MiB

	

188 MiB




Mycroft Kroko

	

160 MiB

	

160 MiB




Slate + clavier (ouverts)

	

35 MiB

	

35 MiB




Mike 350M (runtime léger estimé)

	

300 MiB

	

—




Mannie (pic Claude Code sur Pi)

	

—

	

244 MiB




Total approximatif

	

683 MiB

	

627 MiB




Libre sur 983 MiB

	

300 MiB

	

356 MiB

RAM utilisée
RAM restante
0 MiB
200 MiB
400 MiB
600 MiB
800 MiB
Mike
Mannie

Estimations composites issues de mesures sur plusieurs machines, pas encore validées en charge simultanée sur Luna.

On est donc autour de 30 à 36 % de RAM encore disponible, Slate et clavier compris. En les fermant, on remonte à environ 34 à 40 %.

Ce n'est pas tout à fait 50 %, mais c'est déjà confortable pour de petites applications. Et les chiffres restent prudents à interpréter : les pics mémoire, le partage des bibliothèques, le cache et le comportement réel sur Luna pourront modifier ces résultats.

3. La vraie contrainte devient le harness de Mike

C'est effectivement le chaînon manquant.

Aujourd'hui, ton agent distant pilote déjà Luna via MCP et IPC Sway. Le travail de Mike n'est pas de reconstruire ce système, mais de remplacer le modèle distant par un moteur local extrêmement spécialisé.

Je vois une architecture particulièrement intéressante :

Un routage déterministe pour les commandes triviales.

LFM2.5-350M pour interpréter les commandes moins évidentes.

Un micro-harness qui valide les arguments et traduit les intentions en actions Wyoh.

Une confirmation explicite pour les opérations qui modifient l'état du système.

À la limite, Mike n'a pas besoin de « savoir gérer MCP » au sens large. Son harness peut lui présenter un catalogue réduit d'actions. Le modèle choisit une action et ses paramètres ; le harness s'occupe du protocole, de l'état et des permissions.

C'est beaucoup plus réaliste pour 350 millions de paramètres qu'un agent généraliste devant découvrir et orchestrer arbitrairement des outils MCP.

4. Une conséquence architecturale que je trouve importante

Le Slate ne doit dépendre ni de Mike ni de Mannie.

Il appartient à Wyoh et offre simplement plusieurs destinations pour le texte validé :

application active ;

Mike, pour agir localement ;

Mannie, pour interroger un modèle distant.

Le gestionnaire de sessions peut charger Mike à la demande et libérer sa mémoire quand Mannie prend le relais. Mycroft, lui, peut rester résident pour garder la dictée réactive.

Cette séparation résout également le problème que tu soulevais sur le choix du destinataire avec les boutons physiques.

Au fond, on passe d'une architecture d'agents empilés à une architecture de capacités activées selon l'usage. Et sur une machine de 1 Go, c'est une différence considérable.

Il reste une petite nuance : lorsqu'on est dans Mannie, certaines tâches pourront avoir besoin de piloter Wyoh. Mais Mannie pourra alors utiliser directement son MCP, sans faire tourner Mike. C'est précisément ce qui rend les deux modes indépendants.

## Utilisateur

Alors, là, il y a une petite distinction. C'est-à-dire que le slate est pensé pour dépendre en partie de Mike. Dans le sens où si on va faire une dictée, si on va faire une dictée vocale, on va se retrouver en langage naturel. Or derrière, ce qu'on veut, c'est transformer ce langage naturel en opération, et là c'est Mike. Quoi qu'on fasse, c'est Mike qui fait ça. Mais, enfin, au choix. Soit on dit Mike intervient après, donc il fait pas partie de Slate, et c'est ça, c'est j'envoie à Mike. C'est-à-dire qu'on a déjà commencé à parler de ça, c'est qu'en sortie de Slate, grosso modo, j'ai plusieurs boutons, un bouton qui envoie sur input, un bouton qui envoie à Mike, un bouton qui envoie en ligne de commande, je sais plus, mais quelque chose dans le genre. En sachant qu'envoyer en ligne de commande, c'est peut-être envoyer à Mike tout bêtement. Ou peut-être un bouton qui envoie à Mani, mais je suis pas sûr, parce que pour moi, Mani, c'est une application lourde. Donc grosso modo, c'est input. Quand j'envoie à Mani, c'est que j'envoie sur input. Donc au choix, c'est peut-être soit j'envoie à Mike, soit j'envoie sur input. Et donc, ça veut dire qu'à des moments, j'ai un Slate qui est démarré avec ou sans Mike, où Mike, c'est juste la sortie du Slate. Ouais non, c'est envoyer du Slate, c'est la sortie. Bon, à part que si j'ouvre le Slate à partir de Mani, je dois pas pouvoir envoyer mon input vers Mike. Si j'ouvre le Slate à partir du command line, clairement, je veux pouvoir traduire mon input en vrai command line, vérifier la syntaxe, etc., que c'est cohérent avec ce qu'il y a autour et tout, et potentiellement me dire non, ou est-ce que c'est vraiment ça que tu veux faire, etc. Donc peut-être qu'il y a un passage genre je fais une sortie validée par Mike, avec, voilà, j'ai dit que je voulais faire un ls du home dir. Quand je dis je veux faire un ls du home dir, Mike doit le traduire dans ls tilde et pas autre chose.

## Assistant

Je crois qu'on arrive à une distinction architecturale intéressante : le Slate est un outil de composition, tandis que Mike peut être soit le destinataire de cette composition, soit un interpréteur intermédiaire avant l'application.

Et ces deux usages de Mike sont assez différents.

1. Trois chemins possibles, mais seulement deux opérations de sortie

SLATE

Texte dicté ou saisi, éditable

Choisir la sortie

Input

Application active

Envoi du texte tel quel

Mike

Interprétation locale

Action Wyoh ou proposition de commande

Cas A — Mannie est ouvert

Tu dictes : « Regarde ce fichier et propose-moi une correction. »

Le Slate injecte le texte dans l'input de Claude Code. Mike n'intervient pas. Mannie possède déjà sa propre intelligence et son propre harness.

Cas B — Tu es sur le bureau Wyoh

Tu dictes : « Ouvre la calculatrice. »

Le Slate envoie le texte à Mike, qui traduit en launch_app("calculator"), puis Wyoh effectue l'action après validation.

Cas C — Tu es dans un terminal

Tu dictes : « Liste les fichiers de mon répertoire personnel. »

Mike traduit en une proposition :

Commande proposée

ls ~

Copier

Lister le contenu du répertoire personnel, sans modifier les fichiers.

Lecture seule
À valider

Ici, Mike ne pilote pas directement une opération Wyoh. Il produit du texte destiné à l'application, avec une interprétation sémantique et une vérification.

C'est une capacité bien plus générale que les sept outils actuellement testés.

2. Je distinguerais « destinataire » et « transformation »

Je pense que c'est la clé pour ne pas compliquer l'interface.

	

Destinataire

	

Transformation




Mannie ouvert

	

Input de Mannie

	

Aucune




Terminal ouvert, commande littérale

	

Input du terminal

	

Aucune




Terminal ouvert, langage naturel

	

Input du terminal

	

Mike traduit en shell




Bureau Wyoh

	

Wyoh / MCP

	

Mike traduit en action

On pourrait donc conserver deux actions de sortie :

Input : transmettre exactement ce que contient le Slate.

Mike : demander une interprétation adaptée au contexte, puis présenter la proposition à valider.

Mike utilise l'état de Wyoh pour savoir si la destination est un terminal, le bureau ou autre chose.

Cela évite d'introduire un bouton spécifique « Shell » qui serait finalement un doublon de Mike.

3. Mais Mike doit connaître le contexte

C'est là que l'IPC Sway et le harness deviennent essentiels.

Quand le Slate appelle Mike, il devrait lui transmettre non seulement la phrase, mais également un contexte structuré, par exemple :

JSON
{
  "text": "liste mon répertoire personnel",
  "context": {
    "focused_app": "foot",
    "app_type": "terminal",
    "cwd": "/home/michael",
    "shell": "bash"
  },
  "requested_output": "proposal"
}

Attention, Sway connaît la fenêtre active, mais pas automatiquement le répertoire courant ni l'état du shell. Il faudra un adaptateur terminal pour enrichir ce contexte ; faute de quoi Mike devra simplement déclarer ces informations inconnues.

Le résultat de Mike pourrait ensuite être :

JSON
{
  "type": "terminal_command",
  "command": "ls ~",
  "explanation": "Liste le répertoire personnel",
  "requires_confirmation": true
}

Le harness vérifie que la sortie respecte le contrat. Pour les commandes shell, il faudra une politique de vérification distincte : un modèle de 350M ne peut pas garantir, à lui seul, qu'une commande arbitraire est sûre.

4. Ce que je proposerais pour le Slate V1

À mon sens, on peut conserver une interface remarquablement simple :

Le Slate s'ouvre, permet de dicter ou taper, puis propose deux sorties : Input et Mike.

Input est toujours disponible.

Mike est disponible seulement si le modèle local est actif ou peut être chargé.

Lorsque Mannie occupe la mémoire, l'accès à Mike peut être désactivé.

La sortie de Mike est une proposition, jamais une exécution implicite.

Après validation, cette proposition est soit injectée dans la fenêtre cible, soit exécutée par une action Wyoh autorisée.

Et je distinguerais bien valider la proposition et exécuter la commande. Par exemple, pour ls ~, Mike peut faire apparaître la commande dans le terminal sans envoyer Enter. Cela laisse une dernière possibilité de correction.

L'intérêt est que le Slate n'a pas besoin d'embarquer un modèle ou de connaître les outils MCP. Il sait simplement envoyer le texte à un processeur local, puis afficher et accepter son résultat.

Il y a toutefois une question fonctionnelle qui me paraît plus importante que le choix des boutons : veux-tu que Mike puisse travailler en plusieurs tours depuis le Slate ?

Parce que traduire « liste mon home » en ls ~ ne demande qu'une inférence. Mais « trouve-moi le dernier fichier que j'ai modifié et ouvre-le » nécessite potentiellement d'interroger le système, de récupérer un résultat et de prendre une deuxième décision.

C'est là qu'on passe d'un traducteur d'intention à un véritable agent local, et que le design du micro-harness devient déterminant.

## Utilisateur

Je voudrais que tu recharges le projet. Je viens de toucher de la documentation qu'on a fait, donc qui va donner à peu près l'état d'avancement du projet. J'ai aussi touché le logbook qui est dedans avec. Donc regarde un peu, regarde un peu le projet et on en discute après.

## Assistant

J'ai tenté de recharger TANSTAAFLLM depuis GitHub, mais je n'ai pas encore pu accéder à la nouvelle documentation ni au logbook.

Le dépôt que nous avions identifié est 
mdussere/tanstfaafllm
. Il n'apparaît actuellement pas parmi les dépôts accessibles à mon connecteur GitHub.

En revanche, j'ai toujours le contexte de nos dernières discussions.

État du projet que je connais

Composant

	

Dernier état connu




Luna

	

R36 Ultra, Arch-R modifié, Wi-Fi fonctionnel




Wyoh

	

Interface Sway/Wayland, travail sur les interacteurs physiques




Mycroft

	

ASR local Sherpa-ONNX, saisie vocale avec tampon éditable




Slate

	

Interface de composition des commandes, routage vers application, Mike ou Mannie à définir




Mike

	

Agent local frugal, architecture encore en développement




Mannie

	

Agent de développement utilisant une API de modèle distant




MCP

	

Exposition de l'IPC Sway pour piloter l'environnement




Luna-Pi

	

Plateforme Raspberry Pi de développement et de validation

Notre dernière discussion portait notamment sur la distinction entre ouvrir le Slate, composer une entrée et choisir sa destination, avec les boutons physiques de la console.

Mais cet état est issu de nos échanges, pas de tes dernières modifications.

Pour récupérer le nouvel état

Il faudrait que tu rendes le dépôt TANSTAAFLLM accessible au connecteur GitHub dans ses paramètres d'accès aux dépôts. Si tu viens de modifier les documents localement, il faut également qu'ils soient poussés sur GitHub.

Une fois cet accès rétabli, je pourrai lire les documents et le logbook, puis reconstituer précisément l'architecture implémentée, les décisions prises et les travaux en cours, sans confondre nos anciennes intentions avec ce qui fonctionne réellement.

Je n'ai rien modifié au projet.

## Utilisateur

J'ai corrigé la typo qu'il y avait dans le nom du... dans le nom du projet. Il y avait un F en trop, donc corrige.

## Assistant

Le nom corrigé est TANSTAAFLLM (There Ain’t No Such Thing As A Free LLM).

Le dépôt GitHub est donc désormais :

https://github.com/mdussere/tanstaafllm

Je retiens cette orthographe pour la suite du projet.

## Utilisateur

Bon maintenant t'es corrigé, va voir le dépôt et regarde ce qu'il y a, ce qui est neuf, etc.

## Assistant

J'ai retrouvé le bon dépôt : 
mdussere/tanstaafllm
, et cette fois l'accès fonctionne.

Il y a eu beaucoup de changements depuis notre dernière discussion. Le dernier commit, c1b92b2 du 11 octobre 2026, est précisément la grosse mise à jour documentaire dont tu me parlais.

1. Le projet a franchi une étape importante

Ce n'est plus seulement une exploration du matériel R36 Ultra et une architecture théorique d'agents. Luna est maintenant une petite machine Linux avec un environnement graphique fonctionnel, pilotable aux boutons, et une première intégration de l'interface vocale.

Avancement par composant

État documenté au 11 octobre

Luna

Matériel et OS opérationnels

Wyoh

Desktop, boutons, Slate et applications

Mycroft

Intégré, microphone bloquant

Mike

Benchmarks sur machine de développement

Mannie

Expérimenté sur luna-pi

Lecture qualitative de l'avancement, pas un pourcentage d'achèvement.
Les changements concrets que je retiens

Luna : ArchR fonctionne avec le Wi-Fi corrigé, Sway utilise le GPU Mali, et le bureau se lance au démarrage. Le stockage a été réorganisé.

Wyoh : les boutons contrôlent les fenêtres, le pointeur est déplacé au stick droit, un menu d'applications existe, le Slate est présent et un clavier AZERTY virtuel est intégré. Le bureau gère quatre fenêtres en mosaïque.

Applications : calculatrice style Windows 3.1, gestionnaire de fichiers à deux panneaux et Wolfenstein 3D sont fonctionnels. Échecs, Dino et NetSurf sont prévus.

Mycroft : le modèle français Sherpa-ONNX est désormais intégré au système de dictée du Slate. Les problèmes d'affichage de la console ont été corrigés.

Mike : le rôle se précise : petit modèle local proposant une action à valider, avec LFM2.5-350M parmi les candidats.

Mannie : son rôle dépasse désormais le développement. Il devient aussi le modèle distant auquel Mike peut escalader les requêtes difficiles.

La principale limite fonctionnelle reste le microphone : Mycroft est installé et câblé, mais il n'a pas encore d'entrée audio utilisable sur Luna.

2. Les nouveautés les plus intéressantes
Le modèle ASR Kroko change la donne

C'est probablement le résultat expérimental le plus intéressant de la journée.

Sherpa Zipformer actuel

13,4 %
WER sur ta lecture française

216 MiB

Mémoire, machine de développement

Kroko French

9,1 %
WER sur la même lecture

160 MiB

Mémoire, machine de développement

Kroko est plus léger, utilise environ moitié moins de CPU dans le benchmark de référence et produit directement majuscules et ponctuation. Tu l'as essayé vocalement sur Termidor et tu as validé la qualité.

La prochaine expérience décisive est son exécution sur Luna, où il pourrait enfin permettre de suivre la parole en temps réel. Le temps de chargement reste un obstacle, d'où la décision de garder Mycroft résident.

Le budget mémoire devient une contrainte architecturale mesurée

Élément

	

RAM approximative




Bureau Sway + barre + fond

	

46 MiB




Daemon gamepad

	

17,5 MiB




Slate + clavier, ouverts

	

35 MiB




Mycroft actuel, sur Luna

	

252 MiB




Mycroft Kroko, sur Pi

	

159 MiB




Mike 350M, sans Python (estimé)

	

300 MiB




Mannie Claude Code, pic sur Pi

	

244 MiB

Les mesures sont faites sur plusieurs machines : elles ne constituent pas encore un profil complet de consommation simultanée sur Luna.

On voit néanmoins que le trio Mycroft–Mike–Mannie sera difficile à faire cohabiter avec seulement 983 MiB de RAM. La gestion du cycle de vie des modèles et des services sera aussi importante que leur optimisation.

L'organisation en agents est devenue une vraie méthode de développement

C'est un autre changement majeur, moins visible sur la console.

Tu as maintenant six worklines séparées, chacune avec son plan, ses tests, ses résultats et son historique. Professor coordonne les dépendances et arbitre l'accès exclusif à Luna.

Le protocole 🟩 go Step N, les tests pytest/Gherkin, les captures inspectées et le logbook forment un véritable processus de développement multi-agents, plutôt qu'une accumulation de sessions de coding.

Tu as également clarifié deux décisions importantes : Adam est mis en attente, et les rôles initiaux de Mike (local) et Mannie (distant) ont été rétablis après leur inversion temporaire.

3. Ce qui reste ouvert

À la lecture de docs/LOGBOOK.md, les sujets prioritaires sont désormais assez bien délimités.

Sujet

	

Situation




Microphone

	

USB-C avec véritable périphérique audio attendu




ASR temps réel

	

Kroko à mesurer directement sur Luna




Mike local

	

LFM2.5-350M retenu, déploiement et contrat d'actions encore à finaliser




Mannie

	

Claude Code validé sur Pi ; essai sur Luna à venir




Slate

	

Dictée intégrée ; routage vers application, Mike ou Mannie encore à construire




Wi-Fi graphique

	

Panneau de configuration à développer




Comptes Linux

	

Les sessions tournent encore comme root




Documentation

	

Architecture et composants rédigés ; guide utilisateur et procédures à suivre

4. Mon premier regard sur la direction du projet

Je vois trois évolutions de fond.

D'abord, Wyoh devient le socle réel de l'ordinateur AI-native. Ce n'est pas un simple habillage graphique : le gamepad, le Slate, les applications et l'IPC Sway constituent une même interface exploitable par une personne et par des agents.

Ensuite, le principe du least sufficient intelligence commence à prendre une forme concrète : boutons et règles déterministes d'abord, modèle local ensuite, modèle distant en dernier recours. Les résultats de Mike montrent aussi que cette stratégie a des limites mesurables : environ deux tiers des requêtes inédites sont correctement traitées avec le routage actuel.

Enfin, le problème initial « faire fonctionner Linux sur une console à 30 € » est essentiellement derrière nous. Le vrai sujet devient maintenant l'orchestration des capacités dans 1 Go de RAM, sans sacrifier l'interactivité ni le contrôle utilisateur.

Le point que je voudrais particulièrement discuter avec toi est le contrat entre le Slate, Wyoh et Mike : il me semble que c'est là que se décide la différence entre une petite machine Linux commandée à la voix et un véritable environnement AI-native.

J'ai maintenant relu le guide d'architecture, les cinq fiches des composants et le logbook récent. Nous pouvons reprendre sur cette base.

Références : 
Guide du projet
 · 
Architecture
 · 
Logbook
 · 
Dernier commit documentaire

## Utilisateur

Uploaded an image

## Assistant

Ta capture confirme que la configuration GitHub est correcte.

 Read and write sur le code, les issues, les pull requests et les workflows.

 Le dépôt mdussere/tanstaafllm est explicitement autorisé.

 L'application ChatGPT Codex Connector est installée.

Il n'y a donc rien à modifier sur cette page.

Le problème semble être côté ChatGPT : la première création d'issue a fonctionné, mais les tentatives suivantes ont été bloquées par ses contrôles de sécurité, avant même d'atteindre GitHub.

Je te propose de vérifier les autorisations du plugin dans ChatGPT → Paramètres → Plugins → GitHub. En particulier, regarde si les actions d'écriture nécessitent une confirmation ou sont soumises à des restrictions.

Ne révoque pas l'installation GitHub : elle semble correctement configurée.

## Utilisateur

Retry

## Assistant

Nouvel essai : toujours bloqué.

J'ai retenté la modification de l'
issue #2 — Mycroft English ASR
, avec le lien vers notre conversation et la consigne d'en extraire les verbatims en première étape.

Même erreur :

This tool call was blocked by OpenAI's safety checks.

Diagnostic : les permissions GitHub sont correctes d'après ta capture. Le blocage intervient au niveau des contrôles de sécurité ChatGPT, pas de l'authentification GitHub.

L'issue #2 reste inchangée.

## Utilisateur

Retry

## Assistant

Toujours bloqué.

Nouvel essai de mise à jour de l'
issue GitHub #2
.

Même erreur :

This tool call was blocked by OpenAI's safety checks.

L'issue reste inchangée. Le blocage provient des contrôles de sécurité de ChatGPT, malgré les permissions GitHub correctes.

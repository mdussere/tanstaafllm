# ChatGBC / Rei — note de lecture et d'analyse

**Workline Adam — 31 octobre 2026**  
**Objet :** comprendre les idées du projet de Rudy et les rapprocher de notre réflexion sur l'intelligence embarquée, **sans ouvrir de chantier d'implémentation**.

## 1. Pourquoi ce travail mérite l'attention

Avec [ChatGBC](https://github.com/crashtheuniverse/chatgbc), Rudy a construit et optimisé un modèle de langage qui fonctionne sur Game Boy Color, jusqu'à proposer avec **Rei** une expérience conversationnelle. C'est une démonstration particulièrement inspirante d'ingénierie sous fortes contraintes : il ne s'agit pas seulement de réduire le nombre de paramètres, mais de concevoir ensemble modèle, représentation numérique, moteur d'inférence et interactions.

La documentation de la version 1.0 présente un modèle à **374 000 paramètres**, trois couches de dimension 64, un cœur récurrent **minGRU**, des poids ternaires, et un état récurrent de **192 octets**. L'inférence est réalisée avec des opérations entières adaptées au processeur SM83, sans attention ni cache KV. Rudy indique environ **0,46 s/token** sur la console. Ces chiffres sont ceux publiés par l'auteur et décrivent son environnement de mesure.

## 2. Ce que sait faire le modèle seul

Le modèle d'histoires apprend à prolonger des séquences de texte dans le domaine simplifié de TinyStories. Rei utilise le même type de moteur avec un modèle entraîné pour des dialogues élémentaires. Le réseau prédit des tokens, produit des réponses courtes et conserve un **état récurrent compact** : cet état n'est pas une base de faits exacte ni une archive textuelle de toute la conversation.

Il faut donc distinguer **la fluidité ou la continuité locale du dialogue** de **la restitution fiable d'une information précise entendue longtemps auparavant**. Le second point est pris en charge, en partie, par le logiciel de Rei.

## 3. L'idée la plus féconde : les capacités externalisées

Rei dispose de **quatre tokens particuliers interprétés comme des ordres par le moteur**, plutôt que comme du texte affiché. D'après le README, ils permettent notamment de :
- conserver le dernier mot saisi par l'utilisateur (utilisé, entre autres, pour son prénom) ;
- réafficher le prénom mémorisé ;
- répéter le dernier mot de l'utilisateur ;
- transmettre au modèle, avec la ligne courante, l'information que le prénom est connu.

Le modèle apprend **quand émettre** ces marqueurs ; le programme réalise **exactement** l'opération correspondante. La mémoire du prénom peut persister au-delà de l'extinction de la console. Le fonctionnement conversationnel comprend également une interface, un historique sauvegardé et des comportements d'initiative simples, comme une promenade après une période d'inactivité.

Cette approche ressemble à un **tool calling extrêmement spécialisé et compact** : très peu d'opérations, arguments largement implicites et sémantique exécutée par le runtime. L'analogie avec un « RAG codé en dur » est utile pour imaginer la séparation entre génération et restitution, mais **Rei ne met pas en œuvre un RAG classique** (pas de recherche vectorielle générale, d'embeddings ni de corpus de documents récupérés à la demande).

**Point clé :** Rudy obtient une expérience plus riche en confiant à du logiciel déterministe certaines tâches qu'un modèle minuscule exécuterait difficilement avec fiabilité. Il ne supprime pas la mémoire neuronale : il lui adjoint une mémoire explicite ciblée.

## 4. Une réalisation d'ingénierie de bout en bout

L'autre contribution remarquable est sa démarche de validation : `py/twin5.py` reproduit les règles entières du moteur assembleur (quantification, arrondis, saturations, ordre des opérations et largeurs de calcul). La correspondance entre ce « jumeau » logiciel et la console permet d'optimiser les instructions et les tables tout en vérifiant que les sorties restent identiques. Les tests et mesures de cycles rendent l'évolution reproductible.

La leçon est autant **méthodologique** qu'architecturale : la contrainte matérielle devient un moyen de rendre chaque coût visible et chaque optimisation vérifiable.

## 5. Positionnement dans la littérature

Les références documentées ou discutées dans notre lecture éclairent différentes facettes, **sans prétendre que Rei reproduit à l'identique ces articles** :

- **TinyStories** (Eldan & Li, 2023) : langage cohérent possible avec des modèles très petits sur un domaine simplifié. Rudy cite aussi le modèle TinyStories-260K de Karpathy comme point de départ historique.
- **gbc-transformer** : inspiration initiale mentionnée par Rudy pour l'exécution de modèles sur Game Boy Color.
- **Were RNNs All We Needed?** (2024) : famille des architectures récurrentes simplifiées, dont minGRU.
- **Neural Turing Machines** (Graves et al., 2014) : apprentissage d'accès à une mémoire externe, dans un cadre beaucoup plus général.
- **Toolformer** (Schick et al., 2023) : apprentissage d'appels d'API au moyen d'exemples filtrés puis d'un entraînement supplémentaire.
- **ReAct** (Yao et al., 2022) : alternance raisonnement / action / observation, notamment par exemples dans le contexte sans fine-tuning pour certains modèles.
- **Memorizing Transformers** (Wu et al., 2022) : mémoire externe de représentations internes, mécanisme distinct de l'enregistrement explicite utilisé par Rei.

Le mécanisme précis des quatre opcodes de Rei est documenté par Rudy. Nous n'avons pas établi une filiation directe avec une publication particulière pour cette implémentation.

## 6. Notre conclusion provisoire — sans préjuger de la suite

La valeur de ChatGBC/Rei ne réside pas dans une promesse de connaissances générales ou de commandes système fiables à cette échelle. Elle est dans la **co-conception très économe d'un modèle et d'un environnement capable d'étendre ses possibilités**. C'est un travail positif, inventif et instructif pour TANSTAAFLLM.

Pour situer les idées, **PreStaC** chez Mike vise principalement à éviter de recalculer des états d'inférence ; **Rei** illustre l'intérêt de fonctions et d'une mémoire explicites dans le runtime. Ces mécanismes sont complémentaires, mais non équivalents.

**Question conservée pour notre discussion ultérieure, non traitée dans cette note :** jusqu'où peut-on exploiter les capacités déjà apprises d'un modèle pré-entraîné comme LFM2.5-350M, avec PreStaC et du logiciel déterministe, **sans fine-tuning sur Termidor et sans revenir par défaut à un RAG classique** ? Nous reviendrons ensuite sur les résultats actuels de Mike, notamment son small talk et ses imprécisions factuelles. **Aucune implémentation ni mission à une autre workline n'est décidée ici.**

## Sources

- [Rudy — ChatGBC, README et code](https://github.com/crashtheuniverse/chatgbc)
- [Jumeau d'inférence entier `py/twin5.py`](https://github.com/crashtheuniverse/chatgbc/blob/main/py/twin5.py)
- [Mike — client, caches et PreStaC](https://github.com/mdussere/tanstaafllm/blob/main/docs/16_mike-harness-and-caches.md)
- [Mike — résultats small talk sur Termidor](https://github.com/mdussere/tanstaafllm/blob/main/worklines/mike/docs/1201_01_smalltalk-desk-result.md)
- [Mike — résultats small talk sur Luna](https://github.com/mdussere/tanstaafllm/blob/main/worklines/mike/docs/1205_01_smalltalk-on-luna.md)
- [Neural Turing Machines](https://arxiv.org/abs/1410.5401)
- [Toolformer](https://arxiv.org/abs/2302.04761)
- [ReAct](https://arxiv.org/abs/2210.03629)
- [Memorizing Transformers](https://arxiv.org/abs/2203.08913)

# 0001 — Analyse de la discussion initiale

## Objet et périmètre

Cette note synthétise la conversation initiale sur l'usage d'un Raspberry Pi inutilisé dans le projet **TANSTAAFLLM**. Elle distingue les éléments effectivement établis dans l'échange des recommandations ou hypothèses qui devront être validées sur la machine.

Les quatre images partagées dans la conversation n'étaient pas récupérables dans l'export texte ; leur contenu ne peut donc pas être pris comme une donnée établie ici.

## Résumé exécutif

Le Raspberry Pi doit être envisagé prioritairement comme une petite appliance ARM, permanente et sobre, plutôt que comme une machine d'inférence LLM ambitieuse. Le rôle le plus prometteur identifié est celui de **cible de prototypage et de référence** pour le futur appareil « Luna », et potentiellement de nœud d'orchestration d'un système LLM hybride : stockage, collecte, outils, planification et API localement ; raisonnement lourd par API distante si nécessaire.

Le nom proposé pour ce prototype est `luna-pi`. L'accès d'administration prévu est SSH ; Raspberry Pi Connect est volontairement relégué à un éventuel accès de secours.

## Éléments matériels

### Informations rapportées

| Sujet | État | Détail |
| --- | --- | --- |
| Machine | à confirmer | Elle est décrite d'abord comme un Raspberry Pi 4 avec 4 Go, puis comme un Pi 4B dont les spécifications ne sont pas disponibles. |
| Ancien usage | rapporté | Elle aurait servi professionnellement à booter ou provisionner des serveurs dans un datacenter. |
| Refroidissement | observé/interprété | Un gros radiateur avec deux ventilateurs est mentionné ; cela est cohérent avec un usage continu, mais ne renseigne pas de façon fiable sur la RAM. |
| Mémoire probable | hypothèse | 2 Go est considéré comme plausible, 4 Go possible en cas de standardisation. Aucune valeur n'est vérifiée. |

### Conséquences retenues

- Il ne faut pas fonder l'architecture sur l'hypothèse de 4 Go avant vérification matérielle.
- Une cible de 2 Go reste utile : elle est assez confortable pour développer des services légers tout en rapprochant l'environnement des contraintes de Luna, annoncée à 1 Go.
- Les priorités sont donc la sobriété mémoire, un fonctionnement fiable 24/7 et des services simples à observer, plutôt que la taille maximale du modèle local.

### Vérifications à faire avant de figer la suite

1. Identifier précisément le modèle, la quantité de RAM et le stockage disponible.
2. Relever l'OS, la version du noyau, l'architecture et les températures au repos/en charge.
3. Vérifier l'alimentation, le réseau et le comportement des ventilateurs.
4. Établir un budget mémoire et CPU réel avant de sélectionner des modèles ou de multiplier les services.

## Rôle du Raspberry Pi dans le projet

### Orientation privilégiée

Le rôle conseillé n'est pas de faire tourner « le plus gros Llama possible », mais de transformer la machine en **LLM appliance**. Cette appliance peut rester allumée en continu et assurer les fonctions qui profitent d'une présence locale, sans exiger un gros GPU :

- API locale, par exemple FastAPI ;
- planification de tâches et exécution périodique ;
- stockage léger, par exemple SQLite ;
- collecte de sources et persistance ;
- embeddings, indexation ou clustering à petite échelle ;
- exposition d'outils à un modèle distant ;
- métriques, journalisation et expérimentation.

Le raisonnement coûteux peut être délégué à une API de LLM. Cette séparation rend le système utile même si l'inférence locale est lente ou limitée par la RAM.

### Position dans l'architecture Luna

L'architecture conceptuelle retenue dans l'échange est :

```text
luna-pi  = cible de référence et de prototypage
luna     = cible finale, handheld RK3326
```

`luna-pi` n'est donc pas une machine jetable avant l'arrivée de Luna. Il doit pouvoir rester le banc de développement, de validation et de comparaison de la cible finale. Cette continuité justifie de documenter les écarts matériels et de tester tôt sous contraintes.

## Pistes fonctionnelles évoquées

### 1. Inférence locale légère

Cette piste est considérée comme intéressante pour apprendre et mesurer, mais non comme l'objectif principal.

- Outil proposé : `llama.cpp`.
- Formats envisagés : modèles GGUF quantifiés.
- Ordre de grandeur évoqué pour un Pi 4/4 Go : modèles de 0,5 à 1,5 milliard de paramètres ; 3B en Q4 éventuellement, mais avec lenteur et pression mémoire.
- Candidats cités : Qwen 2.5 0.5B / 1.5B, SmolLM2 1.7B, TinyLlama 1.1B.

Les expériences à mener pourraient comparer tokens/s, quantification, consommation de RAM, température CPU, taille de contexte et paramètres de génération. Tool calling simplifié, embeddings et tokenisation sont aussi cités comme sujets d'apprentissage.

Ces tailles et performances sont des estimations de discussion, pas des benchmarks validés sur la machine réelle.

### 2. Mini-Scout domestique — piste recommandée

Le projet conseillé en priorité est un pipeline local de veille/agrégation, inspiré d'un cycle :

```text
collecte → embeddings → clustering → nommage → agrégation/résumé
```

Sources possibles : flux RSS, quelques pages Web, documents locaux, et éventuellement MQTT/domotique. Le Pi stocke et prépare les données ; un LLM peut nommer et résumer les groupes d'information.

Cette piste est cohérente avec les capacités de la machine et permet de travailler simultanément la persistance, la planification, les embeddings, le clustering, le RAG, les API, les agents et l'évaluation.

### 3. Orchestration multi-agent

Une autre idée consiste à faire tourner plusieurs services Docker avec des rôles, mémoires et outils distincts. Ils répondraient indépendamment à une question, se critiqueraient, puis un agent final arbitrerait.

Le Pi serait l'orchestrateur ; les modèles eux-mêmes pourraient être appelés par API. Cette proposition n'est pas encore un choix de projet ni une architecture validée.

### 4. Assistant vocal matériel

Le scénario matériel envisagé est :

```text
micro → Whisper / whisper.cpp → LLM → outils → Piper TTS → enceinte
```

La reconnaissance et la synthèse vocales pourraient être locales, tandis que le raisonnement passerait par une API. Cette idée reste exploratoire ; aucun choix de microphone, d'enceinte, de modèle STT/TTS ou de latence cible n'a été arrêté.

## Identité et nommage

### Nom du prototype

Le nom `luna-pi` est la proposition privilégiée. Il désigne explicitement le prototype Raspberry Pi de Luna, sans le confondre avec la cible finale.

| Élément | Proposition |
| --- | --- |
| Nom et hostname du prototype | `luna-pi` |
| Produit/cible finale | `luna` |
| Plateforme finale annoncée | handheld RK3326 |

Des alternatives ont été mentionnées — `luna-proto`, `little-luna`, `luna-0`, `luna-earth`, `terraluna` — mais aucune ne supplante `luna-pi`. `terraluna` est explicitement déconseillé, car le nom évoque la crypto.

### Domaine

L'achat d'un domaine est envisagé par l'utilisateur. Aucun nom de domaine, fournisseur, finalité ni décision d'achat n'est établi dans cette conversation.

## Accès distant et exploitation

### Décision d'orientation

Le chemin d'accès normal prévu est :

```text
PC / Codex
    │
   SSH
    │
    ▼
 luna-pi
```

SSH est préféré parce qu'il est standard, léger, automatisable et proche de l'accès qui sera utilisé avec Luna. Il doit constituer la base de l'administration, du déploiement et de l'automatisation.

### Raspberry Pi Connect

Raspberry Pi Connect est identifié comme un service officiel d'accès distant depuis un navigateur, avec shell et, pour un système de bureau, partage d'écran. Il n'est pas retenu comme dépendance initiale de TANSTAAFLLM.

Son rôle acceptable serait un accès de secours — par exemple depuis un téléphone — si ce besoin se confirme. Son activation n'est donc ni nécessaire ni prioritaire au démarrage.

## Décisions, recommandations et sujets ouverts

| Catégorie | Élément | Statut |
| --- | --- | --- |
| Nom | Utiliser `luna-pi` pour le prototype | proposition fortement privilégiée ; à confirmer explicitement |
| Rôle | Conserver le Pi comme cible de référence/prototypage | orientation établie |
| Accès | Utiliser SSH comme voie principale | orientation établie |
| Connect | Ne pas l'ajouter aux dépendances initiales | recommandation retenue |
| Charge LLM | Privilégier l'orchestration et les services légers au gros modèle local | orientation établie |
| Premier cas d'usage | Explorer un mini-Scout domestique | recommandation prioritaire, pas encore décision de réalisation |
| Hardware | RAM exacte, stockage, état de la machine | non vérifiés |
| Inference | modèle, quantification, runtime et métriques | non choisis |
| Infra | Docker, FastAPI, SQLite, schéma de données et API externe | suggérés, non validés |
| Domaine | achat, nom et usage | ouvert |

## Plan de démarrage cohérent avec la discussion

1. Inventorier le matériel et installer/configurer l'OS minimal.
2. Fixer le hostname `luna-pi` si le nom est confirmé.
3. Mettre en place l'accès SSH par clés et documenter la connexion depuis le poste de développement.
4. Mesurer les ressources disponibles et, seulement ensuite, tester un petit modèle local quantifié avec `llama.cpp`.
5. Choisir un premier vertical simple : collecte RSS + SQLite + résumé distant, par exemple.
6. Ajouter progressivement embeddings, clustering et automatisation, en mesurant mémoire, température, latence et fiabilité.
7. Garder le système suffisamment léger et reproductible pour qu'il serve de référence à Luna.

## Limites de cette synthèse

- Elle décrit ce qui a été dit, pas l'état réel de la machine.
- Les recommandations de modèles, de mémoire et de performances doivent être revalidées par des tests sur `luna-pi`.
- Les images de la conversation ne sont pas analysées.
- Aucun choix définitif de produit, de stack complète, de domaine ou de fournisseur de LLM n'a été acté.

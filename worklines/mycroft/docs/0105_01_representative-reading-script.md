# Representative French reading script for Mycroft

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** mycroft 1.5 ✅
**Status:** prepared; recording and evaluation are pending.
**Question answered:** What short, consented reading exercises representative CLI, code-editing, interface-navigation, and ordinary French ASR vocabulary?
## Recording rules
- Read only the words after each number and long dash, in one continuous take.
- Do not read headings, comments, numbers, punctuation names, or the phrase ground truth aloud.
- Leave a natural short pause between groups; do not stop the recorder between them.
- Use a quiet, normal working-room environment and a normal working pace.
- If possible, export mono WAV, 16 kHz, signed 16-bit PCM. Otherwise send the original WAV unchanged and report its sample rate.
- The speaker consents to use of this WAV only for Mycroft evaluation. The recording remains outside the repository unless a separate retention decision is made.
The canonical reference is the final section. The identifiers and comments exist only to discuss recognition errors precisely.
## 01 — Interactions dans la CLI
<!-- Tests commands spoken aloud, files, diagnostics, failure reporting, and a safety boundary. -->
- **01.1** — Dans le terminal, lance git status, puis résume les fichiers modifiés sans rien écrire.
- **01.2** — Affiche README point markdown, puis cherche l'expression mémoire partagée sans modifier le fichier.
- **01.3** — Lance le test avec le fichier WAV fourni, conserve la sortie normale dans un fichier temporaire et garde les diagnostics sur la sortie d'erreur.
- **01.4** — Si la commande échoue, donne le code de retour et propose une vérification réversible, sans téléchargement ni suppression.
## 02 — Édition de code
<!-- Tests source-file names, code vocabulary, controlled editing, diffs, and test language. -->
- **02.1** — Ouvre benchmark underscore ASR point py, repère la fonction qui calcule le WER et explique ce que signifie son résultat.
- **02.2** — Modifie uniquement le commentaire de la fonction, remplace provisoire par mesuré, puis affiche la différence avant d'écrire.
- **02.3** — Ajoute un test pour un transcript vide, mais n'exécute rien tant que les enregistrements privés ne sont pas exclus.
## 03 — Navigation dans l'interface
<!-- Tests directional interaction, selection, dialogs, visible state, and cautious observation. -->
- **03.1** — Dans l'interface, va vers la droite jusqu'au panneau des actions, sélectionne le document Mycroft, puis ouvre son état.
- **03.2** — Si une boîte de dialogue apparaît, lis les choix disponibles avant de confirmer ou d'annuler.
- **03.3** — Reviens à l'écran précédent, cherche l'élément nommé résultats, et annonce ce qui est visible sans deviner ce qui est caché.
## 04 — Usage courant et cas difficiles
<!-- Tests connected French, constrained-hardware reasoning, and uncommon proper nouns. -->
- **04.1** — Je veux une réponse courte et précise ; si une information manque, dis-le franchement plutôt que de compléter par une supposition.
- **04.2** — TANSTAAFL signifie qu'un modèle plus précis n'est pas gratuit s'il coûte trop de RAM, de stockage ou de secondes au démarrage sur Luna.
- **04.3** — Le conseil territorial de Saint-Pierre-et-Miquelon examine quatre tombeaux de la dynastie achéménide et sept monuments sassanides.
## Canonical ground truth
Do not read this duplicate section during the recording. It is the exact reference transcript, in reading order.
> Dans le terminal, lance git status, puis résume les fichiers modifiés sans rien écrire.
> Affiche README point markdown, puis cherche l'expression mémoire partagée sans modifier le fichier.
> Lance le test avec le fichier WAV fourni, conserve la sortie normale dans un fichier temporaire et garde les diagnostics sur la sortie d'erreur.
> Si la commande échoue, donne le code de retour et propose une vérification réversible, sans téléchargement ni suppression.
> Ouvre benchmark underscore ASR point py, repère la fonction qui calcule le WER et explique ce que signifie son résultat.
> Modifie uniquement le commentaire de la fonction, remplace provisoire par mesuré, puis affiche la différence avant d'écrire.
> Ajoute un test pour un transcript vide, mais n'exécute rien tant que les enregistrements privés ne sont pas exclus.
> Dans l'interface, va vers la droite jusqu'au panneau des actions, sélectionne le document Mycroft, puis ouvre son état.
> Si une boîte de dialogue apparaît, lis les choix disponibles avant de confirmer ou d'annuler.
> Reviens à l'écran précédent, cherche l'élément nommé résultats, et annonce ce qui est visible sans deviner ce qui est caché.
> Je veux une réponse courte et précise ; si une information manque, dis-le franchement plutôt que de compléter par une supposition.
> TANSTAAFL signifie qu'un modèle plus précis n'est pas gratuit s'il coûte trop de RAM, de stockage ou de secondes au démarrage sur Luna.
> Le conseil territorial de Saint-Pierre-et-Miquelon examine quatre tombeaux de la dynastie achéménide et sept monuments sassanides.

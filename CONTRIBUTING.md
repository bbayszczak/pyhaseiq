# Contribuer

## Périmètre

`pyhaseiq` est une bibliothèque **en lecture seule** et **sans état** pour les poêles Hase IQ
de la génération `Flamemonitor`. Elle interroge le poêle et rend ce qu'il répond. Rien d'autre.

Historisation, moyennes, seuils, notifications, reconnexion automatique : tout cela appartient
à la couche appelante — typiquement une intégration Home Assistant. Les propositions qui font
remonter de l'état ici seront refusées.

## Mise en route

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatage
uv run pytest            # tests — aucun matériel requis, le poêle est simulé
```

Python ≥ 3.13. Toujours passer par `uv`. Le linter est strict sur `src/` (docstrings et
annotations obligatoires) ; les tests en sont dispensés.

## Conventions

- Commits en [Conventional Commits](https://www.conventionalcommits.org/), en anglais.
  `release-please` s'en sert : seuls `feat:` et `fix:` déclenchent une release.
- Documentation en français, code et docstrings en anglais.
- Le protocole est décrit dans [`docs/SPEC-PROTOCOLE-WS.md`](docs/SPEC-PROTOCOLE-WS.md), où
  chaque affirmation porte un statut ✅ validé / 🟡 partiel / ❓ supposé. **Ne codez jamais sur
  la foi d'un point ❓** : validez-le d'abord sur du matériel réel et mettez la spec à jour.
- Les actions GitHub sont épinglées sur des SHA complets ; Dependabot les met à jour. Ne jamais
  revenir à un tag mobile.

## Interdits

Un poêle à bois est un appareil à combustion installé chez quelqu'un. Ces points ne seront pas
fusionnés :

- ⛔ **Aucune écriture vers le poêle.** Aucune commande d'écriture n'a été observée dans le
  protocole, aucune n'est implémentée, et c'est un choix permanent. Une bibliothèque de lecture
  ne peut rien casser ; dès qu'elle écrit, cette garantie disparaît.
- ⛔ **Ne pas balayer de noms de requêtes au hasard** sur un poêle réel. On ignore ce qu'un
  `_req=` inconnu déclenche dans le micrologiciel. Les noms nouveaux se découvrent en observant
  l'application constructeur, pas en devinant.
- ⛔ **Ne pas faire remonter d'état** dans la bibliothèque : ni historique, ni cache, ni
  moyenne, ni reconnexion automatique.
- ⛔ **Ne pas présenter les valeurs lues comme une mesure de sécurité.** Elles sont indicatives
  et ne remplacent aucun détecteur ni aucune obligation d'entretien.

## Conditions juridiques des contributions

En contribuant à ce dépôt, vous acceptez ce qui suit.

1. **Aucun code propriétaire** — vous ne devez soumettre aucun code, micrologiciel ou autre
   élément appartenant au fabricant ou à un tiers. Les contributions doivent être originales ou
   sous une licence compatible avec celle de ce projet.

2. **Aucun matériel protégé** — pas de dumps, de binaires décompilés, de clés cryptographiques,
   ni de contenu obtenu en violation d'un contrat de licence utilisateur (EULA), d'un accord de
   confidentialité (NDA) ou d'une restriction équivalente.

3. **Travail indépendant** — les contributions doivent résulter d'une analyse et d'un
   développement indépendants. Si vous vous êtes appuyé sur de la rétro-ingénierie, elle doit
   avoir été menée licitement et aux seules fins d'interopérabilité.

4. **Compatibilité de licence** — toute contribution est publiée sous la licence du projet. En
   soumettant du code, vous confirmez en avoir le droit.

Toute pull request qui enfreint ces conditions sera rejetée. Les mainteneurs se réservent le
droit de retirer une contribution qui exposerait le projet à un risque juridique.

## Sécurité

Pour signaler une faille, voir [SECURITY.md](SECURITY.md) — jamais une issue publique.

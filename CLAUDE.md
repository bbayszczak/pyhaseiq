# CLAUDE.md

Contexte pour Claude Code sur ce dépôt.

## Le projet

`pyhaseiq` est une bibliothèque **en lecture seule** pour les poêles à bois **Hase iQ de la
génération `flamemonitor`**, via leur WebSocket local. Rien d'autre.

⚠️ **Deux générations portent le nom « Hase iQ ».** Seule l'ancienne, pilotée par l'application
`flamemonitor`, est supportée ; celle de l'application `HASE iQ` n'a jamais été observée. Ne
jamais laisser entendre dans la documentation ou le code que la nouvelle fonctionne.

Le protocole est intégralement décrit dans [`docs/SPEC-PROTOCOLE-WS.md`](docs/SPEC-PROTOCOLE-WS.md),
reconstitué par rétro-ingénierie à partir des captures de [`records/`](records/). Chaque
affirmation y porte un statut ✅ validé / 🟡 partiel / ❓ supposé : s'y référer avant
d'implémenter quoi que ce soit, et ne jamais coder sur la foi d'un point ❓.

## Structure

```
src/pyhaseiq/
  protocol.py    encodage base64 et parsing — fonctions pures, aucune I/O
  client.py      client asynchrone, sérialise le dialogue
  models.py      Phase
  exceptions.py
tests/
  fake.py        faux poêle (serveur WebSocket) rejouant les réponses réelles
docs/
  SPEC-PROTOCOLE-WS.md
records/
  captures Wireshark décodées, une par phase, + extract.py qui les produit
demo.py          script de démonstration, lecture seule
```

## Commandes

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatage
uv run pytest            # tests, sans matériel
uv run demo.py <ip>      # lecture live sur un vrai poêle
```

Toujours passer par `uv`. Python ≥ 3.13, CI sur 3.13 et 3.14.

## Conventions

- **Commits en Conventional Commits**, en anglais. `release-please` s'en sert pour produire le
  CHANGELOG et la version : seuls `feat:` et `fix:` déclenchent une release.
- Documentation en français, code et docstrings en anglais.
- **Logging** : `logging` standard, un `_LOGGER = logging.getLogger(__name__)` par module et
  **aucune configuration** (ni handler, ni niveau, ni format) — l'hôte, typiquement Home
  Assistant, possède les handlers et filtre sur `pyhaseiq.<module>`. Tout en `DEBUG`, en
  formatage paresseux (`_LOGGER.debug("%s = %s", name, value)`), jamais de f-string — les
  règles ruff `LOG` et `G` le vérifient. Les erreurs se lèvent, elles ne se loguent pas :
  loguer *et* lever produit un doublon dans les journaux de l'appelant.
- Le linter est strict (docstrings et annotations obligatoires dans `src/`) ; les tests en sont
  dispensés via `per-file-ignores`.
- Les actions GitHub sont **épinglées sur des SHA complets** (un tag comme `@v4` peut être
  redéplacé sur un autre commit). Dependabot les met à jour ; ne jamais revenir à un tag mobile.
- Dépôt public : `CONTRIBUTING.md` et `SECURITY.md` font foi côté contributeurs, les garder
  cohérents avec ce fichier — notamment la liste des interdits ci-dessous.
- `uv.lock` porte la version du paquet : le workflow de release le resynchronise sur la branche
  de la PR de release. Ne pas l'éditer à la main, lancer `uv lock` après tout changement de
  version ou de dépendance.
- La fusion d'une PR de release publie le paquet sur **PyPI** via le *Trusted Publishing*
  (OIDC) : aucun token d'API n'est stocké, l'autorisation vit dans le *publisher* déclaré côté
  PyPI (dépôt `bbayszczak/pyhaseiq`, workflow `release.yml`). Renommer ce fichier ou le dépôt
  casse la publication tant que le *publisher* n'est pas mis à jour.
- Le workflow de release sépare volontairement `build` et `publish` : `uv build` exécute du
  code tiers (hatchling et ses dépendances) et ne doit jamais tourner dans le job qui porte
  `id-token: write`, sans quoi une dépendance de build compromise pourrait publier sur PyPI.
  Ne pas refusionner ces deux jobs.
- `release-please` tourne sous l'identité d'une **GitHub App** dédiée, jamais sous le
  `GITHUB_TOKEN` : celui-ci ne peut pas ouvrir de PR tant que le réglage « Allow GitHub Actions
  to create and approve pull requests » du dépôt est décoché, et ses écritures ne déclenchent
  aucun workflow — la PR de release n'obtiendrait donc jamais les checks que le ruleset de
  `main` exige et resterait infusionnable. Ses identifiants vivent dans les secrets
  `RELEASE_PLEASE_CLIENT_ID` et `RELEASE_PLEASE_PRIVATE_KEY`. Le premier porte le **Client
  ID** de l'App (`Iv23li…`), pas son App ID numérique : l'entrée `app-id` de l'action est
  dépréciée et `client-id` attend l'autre valeur.
- Le commit qui resynchronise `uv.lock` est créé par **l'API GitHub**, jamais par un
  `git commit` dans le *runner* : `main` exige des signatures vérifiées, or un commit fabriqué
  sur le *runner* n'est pas signé et bloque la fusion de la PR de release. GitHub signe les
  commits passés par son API, et l'appel porte le token de l'App, donc la CI se redéclenche.

## Principes de conception

- **Lecture seule, définitivement.** Aucune commande d'écriture n'a été observée dans le
  protocole et aucune n'est implémentée. C'est la garantie centrale du projet : une
  bibliothèque qui ne fait que lire ne peut rien casser sur un appareil à combustion installé
  chez quelqu'un. Ne jamais l'entamer, même « juste pour tester ».
- **Le client ne connaît aucun état.** Pas de cache, pas d'historique, pas de reconnexion
  automatique. Une connexion perdue reste perdue et l'appelant en ouvre une neuve. Toute
  historisation, moyenne ou politique de reprise appartient à la couche appelante.
- **Dialogue strictement sérialisé.** Le protocole n'a aucun identifiant de corrélation : rien
  ne rattache une réponse à sa requête sinon l'ordre. D'où le verrou dans `Client.get()`. Le
  test `test_concurrent_readings_are_serialised_and_never_swap_answers` garde la propriété — il
  échoue si on retire le verrou.
- **Cœur asynchrone assumé** : le poêle est un serveur WebSocket et la cible est Home
  Assistant. Pas de façade synchrone.

## Pièges du protocole

- **Le préfixe se retire avec `removeprefix`, jamais avec `lstrip`.** `lstrip` prend un
  *ensemble de caractères* : `"appT=appT".lstrip("appT=")` rend `""`. C'est un bug réel corrigé
  ici, gardé par `test_the_prefix_is_removed_as_a_prefix_not_as_a_character_set`.
- **La valeur peut contenir un `=`** : `_oemver` répond `_oemver=AAF_5815=9`. Ne découper que
  sur le premier.
- **Toutes les mesures ne sont pas lisibles dans toutes les phases.** L'application
  constructeur ne demande `appT` et `appAufheiz` qu'en phase `HEATING_UP`, `appP` qu'en phase
  `NOMINAL`. On ignore si le poêle répond hors phase ou se tait — auquel cas l'appel part au
  `ResponseTimeoutError`. Tester la phase avant de lire.
- **La phase `4` n'a jamais été observée** : elle vient de la documentation du poêle.

## À ne pas faire

- ⛔ **Ne jamais implémenter ni envoyer de commande d'écriture** vers le poêle.
- ⛔ **Ne pas balayer de noms de requêtes au hasard** sur un poêle réel : on ignore ce qu'un
  `_req=` inconnu déclenche dans le micrologiciel.
- ⛔ **Ne pas recalculer `appAufheiz` à partir de `appT`.** La corrélation est forte
  (R² = 0,992) mais pas exacte : le poêle y mêle autre chose.
- ⛔ **Ne pas présenter les valeurs lues comme un dispositif de sécurité** — ni dans le code,
  ni dans la documentation. Elles sont indicatives.

## Sécurité

Le poêle n'a **aucune authentification** : son WebSocket est ouvert à tout le réseau local.
C'est un fait matériel, pas une faille de cette bibliothèque. La documentation doit le dire et
rappeler de ne jamais exposer le port `8080` sur Internet.

Les traces ne contiennent ni identifiant, ni clé, ni donnée personnelle : il n'y a rien à
masquer dans les logs, contrairement à d'autres protocoles domotiques. Si une requête porteuse
de secret apparaissait un jour, ce constat serait à revoir.

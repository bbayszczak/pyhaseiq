# pyhaseiq

[![CI](https://img.shields.io/github/actions/workflow/status/bbayszczak/pyhaseiq/ci.yml?branch=main&label=CI)](https://github.com/bbayszczak/pyhaseiq/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/release/bbayszczak/pyhaseiq?label=version)](https://github.com/bbayszczak/pyhaseiq/releases/latest)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

Bibliothèque Python **en lecture seule** pour les poêles à bois Hase IQ, via leur WebSocket
local. Entièrement locale : ni cloud, ni application constructeur, ni compte.

> 🔍 **LECTURE SEULE — cette bibliothèque ne commande rien**
>
> `pyhaseiq` **interroge** le poêle : température, phase de combustion, performance. Elle
> n'écrit rien, ne règle rien, n'allume rien, n'éteint rien. Aucune commande d'écriture n'a été
> observée dans le protocole, **aucune n'est implémentée**, et c'est un choix permanent du
> projet — voir les [interdits](CONTRIBUTING.md#interdits).
>
> Un poêle à bois est un appareil à combustion : sa conduite reste manuelle et relève de son
> utilisateur. Cette bibliothèque **observe**, elle ne se substitue à aucun organe de sécurité.

> ⚠️ **PROJET INDÉPENDANT, SANS AUCUNE AFFILIATION**
>
> `pyhaseiq` n'est **en aucun cas** affilié, soutenu, approuvé ou validé par Hase
> (Hase Kaminofenbau GmbH), ou l'une quelconque de ses filiales, marques, sociétés
> apparentées, sous-traitants ou partenaires. *Hase*, *Hase IQ* et *Flamemonitor* sont des
> marques de leurs titulaires respectifs, citées uniquement pour décrire le matériel avec
> lequel cette bibliothèque communique, à des fins d'interopérabilité.
>
> 👉 **Lisez l'avertissement complet ci-dessous avant toute utilisation.** Il couvre
> l'**absence totale de garantie**, la **garantie constructeur** et les conditions d'usage. En
> utilisant cette bibliothèque, vous reconnaissez les avoir lues et acceptées.

<details>
<summary><strong>⚠️ Avertissement complet — à lire avant toute utilisation</strong></summary>

**Ce projet est totalement indépendant et n'est en aucun cas affilié, soutenu, approuvé
ou validé par Hase (Hase Kaminofenbau GmbH), ou l'une quelconque de ses filiales,
marques, sociétés apparentées, sous-traitants ou partenaires.**

*Hase*, *Hase IQ* et *Flamemonitor* sont des marques de leurs titulaires respectifs.
Elles ne sont citées ici que pour **décrire le matériel avec lequel cette bibliothèque
est susceptible de communiquer**, à des fins d'interopérabilité. Aucun code, aucun
binaire, aucun micrologiciel, aucune clé cryptographique et aucune documentation du
fabricant n'est reproduit ni redistribué dans ce dépôt.

**Nom du projet** — `pyhaseiq` est un nom d'usage choisi pour sa lisibilité. Il
n'emporte aucune affiliation, ne constitue ni une marque, ni une revendication
d'origine, ni une autorisation du titulaire de la marque *Hase*. Cette bibliothèque est
un composant tiers **compatible avec** ce matériel, et rien d'autre.

**Méthode** — le protocole documenté ici a été reconstitué par la seule observation du
dialogue réseau entre l'application constructeur et un poêle acquis légalement, sur une
installation appartenant à l'auteur. Aucune décompilation de micrologiciel, aucune
extraction ni publication de clé cryptographique constructeur n'a été réalisée. Ce
travail relève de l'exception d'interopérabilité (art. L122-6-1 III et IV du Code de la
propriété intellectuelle, directive 2009/24/CE art. 5 et 6).

**Lecture seule** — cette bibliothèque n'émet aucune commande d'écriture vers le poêle.
Elle ne modifie aucun réglage, ne déclenche ni n'interrompt aucune combustion. La
conduite du poêle reste entièrement manuelle et sous la responsabilité de son
utilisateur, conformément à la notice du fabricant.

**Aucun rôle de sécurité** — les valeurs lues sont fournies à titre indicatif. Elles ne
constituent ni une mesure certifiée, ni une alarme, ni un dispositif de sécurité, et ne
remplacent en rien un détecteur de fumée, un détecteur de monoxyde de carbone ou le
ramonage réglementaire de votre installation. **Ne fondez aucune décision de sécurité
sur cette bibliothèque.**

**Usage** — cette bibliothèque est destinée à la lecture d'équipements dont vous êtes
propriétaire ou légitime utilisateur, et à eux seuls.

**Absence de garantie** — ce logiciel est fourni « tel quel », sans aucune garantie
d'aucune sorte, expresse ou implicite, y compris, sans s'y limiter, les garanties de
qualité marchande, d'adéquation à un usage particulier et d'absence de contrefaçon.
Dans les limites permises par le droit applicable, l'auteur ne saurait être tenu
responsable d'un quelconque dommage : dysfonctionnement, détérioration de matériel,
perte de données, ou tout dommage direct ou indirect résultant de l'utilisation de
cette bibliothèque.

**Garantie constructeur** — l'usage de ce logiciel avec votre matériel est susceptible
d'en affecter la garantie. Vérifiez-le avant de l'utiliser.

**Support** — assuré bénévolement, sans engagement de délai ni de résultat.

**Licence** — MIT, voir [LICENSE](LICENSE).

En utilisant cette bibliothèque, vous reconnaissez avoir lu et accepté l'ensemble de
ces conditions.

</details>

---

## Sommaire

- [Quelle génération ?](#quelle-génération-)
- [Démarrage rapide](#démarrage-rapide)
- [État du projet](#état-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Logging](#logging)
- [Développement](#développement)
- [Contribuer](#contribuer)
- [Sécurité](#sécurité)

---

## Quelle génération ?

**Deux générations de poêles portent le nom « Hase IQ »**, et elles ne parlent pas le même
langage. Elles se distinguent à l'application que vous utilisez :

| votre application | génération | `pyhaseiq` |
|---|---|---|
| **`Flamemonitor`** | ancienne | ✅ supportée |
| **`Hase IQ`** | nouvelle | ❌ non supportée |

La nouvelle génération n'a pas été observée et son protocole est inconnu. Rien n'est prévu à ce
sujet, et les retours sont les bienvenus.

Le protocole de l'ancienne est intégralement décrit dans
[`docs/SPEC-PROTOCOLE-WS.md`](docs/SPEC-PROTOCOLE-WS.md), où chaque affirmation porte un statut
✅ validé / 🟡 partiel / ❓ supposé.

---

## Démarrage rapide

Avec [`uv`](https://docs.astral.sh/uv/) et l'adresse IP de votre poêle :

```bash
git clone https://github.com/bbayszczak/pyhaseiq
cd pyhaseiq
uv run demo.py 192.168.1.165
```

`uv` crée l'environnement et installe les dépendances tout seul. `demo.py` **n'écrit rien** :
il affiche un tableau rafraîchi en continu avec la phase du poêle et les mesures disponibles.
C'est le moyen le plus rapide de vérifier que votre poêle répond.

---

## État du projet

🚧 **Alpha.** La lecture fonctionne et le protocole est documenté. L'API peut encore changer.

Les changements de chaque version sont consignés dans le [CHANGELOG](CHANGELOG.md), tenu à jour
automatiquement à partir des messages de commit.

---

## Installation

```bash
pip install pyhaseiq
```

Ou directement depuis le dépôt :

```bash
pip install git+https://github.com/bbayszczak/pyhaseiq
```

## Utilisation

L'API est **asynchrone** : le poêle est un serveur WebSocket, et c'est le modèle qu'attend un
hôte comme Home Assistant.

```python
import asyncio

from pyhaseiq import Client, Phase


async def main() -> None:
    async with Client("192.168.1.165") as stove:
        phase = await stove.get_phase()
        print(phase)  # Phase.HEATING_UP

        if phase is Phase.HEATING_UP:
            print(await stove.get_temperature())  # 163.3 °C dans le foyer
            print(await stove.get_heat_up_percent())  # 53.5 % de la montée en chauffe
        elif phase is Phase.NOMINAL:
            print(await stove.get_performance())  # 69 % de performance de combustion


asyncio.run(main())
```

### Les phases

`get_phase()` rend un [`Phase`](src/pyhaseiq/models.py), qui est un `IntEnum` :

| valeur | nom | signification |
|---|---|---|
| `0` | `Phase.IDLE` | pas de feu, le poêle attend |
| `1` | `Phase.HEATING_UP` | feu en cours, la température monte |
| `2` | `Phase.NOMINAL` | température nominale atteinte |
| `3` | `Phase.NEEDS_WOOD` | il faut recharger en bois |
| `4` | `Phase.BURNING_OUT` | le feu s'éteint, ne plus ajouter de bois |

> ⚠️ **Toutes les mesures ne sont pas lisibles dans toutes les phases.** L'application
> constructeur ne demande `appT` et `appAufheiz` qu'en phase `HEATING_UP`, et `appP` qu'en
> phase `NOMINAL`. On ignore si le poêle répond quand même hors de ces phases ou s'il reste
> muet — auquel cas l'appel se solde par un `ResponseTimeoutError`. **Testez la phase avant de
> lire**, comme le fait l'exemple ci-dessus.

### Les erreurs

Toutes dérivent de `HaseIQError`, ce qui permet de rattraper la bibliothèque entière d'un seul
`except` :

| exception | quand |
|---|---|
| `ConnectionFailedError` | poêle injoignable, ou connexion perdue en cours de dialogue |
| `ResponseTimeoutError` | le poêle n'a pas répondu dans le délai imparti |
| `ProtocolError` | réponse illisible, ou phase inconnue |

Le client **ne se reconnecte jamais tout seul** : il ne conserve aucun état, et la politique de
reprise appartient à l'appelant. Une connexion perdue reste perdue — ouvrez un nouveau client.

### Requêtes brutes

Les requêtes documentées mais non exposées par une méthode typée — les séries de mesures, les
versions du micrologiciel — restent joignables :

```python
await stove.get("_wversion")  # '1.4'
await stove.get("appP30Tx")  # '30'
await stove.get("appP30T[15;29]")  # '41;40;40;40;40;39;...'
```

Les noms sont listés dans [`docs/SPEC-PROTOCOLE-WS.md`](docs/SPEC-PROTOCOLE-WS.md).

### Essayer sans écrire de code

```bash
uv run demo.py 192.168.1.165                      # tableau rafraîchi en continu
uv run demo.py 192.168.1.165 --once               # une seule lecture
uv run demo.py 192.168.1.165 --request _wversion  # une requête brute, répétable
uv run demo.py 192.168.1.165 --debug              # afficher le dialogue WebSocket
```

Exemple de sortie :

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ parameter        ┃ value                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Last update      │ 09/21/26 - 08:51:12   │
│ Phase            │ heating up (1)        │
│ Temperature (°C) │ 163.3                 │
│ Heat-up (%)      │ 53.5                  │
│ Performance (%)  │ —                     │
└──────────────────┴───────────────────────┘
```

## Logging

La bibliothèque utilise le module `logging` standard et **ne configure rien** : ni handler, ni
niveau, ni format. C'est l'application hôte qui décide. Chaque module a son logger, nommé
d'après le paquet — `pyhaseiq.client` — ce qui permet de filtrer au paquet entier comme au
module.

Tout est en `DEBUG` : l'ouverture de la connexion et chaque couple requête / réponse. Les
erreurs ne sont pas loguées, elles sont **levées** ; c'est à l'appelant de décider ce qu'il en
fait.

Dans Home Assistant, via `configuration.yaml` :

```yaml
logger:
  logs:
    pyhaseiq: debug
```

En script autonome :

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Exemple de trace :

```
DEBUG pyhaseiq.client: connecting to ws://192.168.1.165:8080
DEBUG pyhaseiq.client: appPhase = 1
DEBUG pyhaseiq.client: appT = 163.3
DEBUG pyhaseiq.client: appAufheiz = 53.5
```

Le poêle n'expose ni identifiant, ni clé, ni donnée personnelle : une trace `DEBUG` peut être
jointe telle quelle à un rapport de bug.

## Développement

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatage
uv run pytest            # tests — aucun matériel requis, le poêle est simulé
```

---

## Contribuer

Les retours sont bienvenus, en particulier sur **d'autres modèles de poêles** et sur la
génération pilotée par l'application `Hase IQ`, jamais observée.

- **Signaler un bug ou proposer une évolution** —
  [ouvrir une issue](https://github.com/bbayszczak/pyhaseiq/issues/new/choose), en précisant
  l'application avec laquelle vous pilotez habituellement votre poêle.
- **Proposer du code** — périmètre, conventions et interdits sont décrits dans
  [CONTRIBUTING.md](CONTRIBUTING.md), à lire avant d'ouvrir une pull request.

---

## Sécurité

Le poêle expose un **WebSocket non chiffré et sans aucune authentification** sur le port
`8080` : toute machine de votre réseau local peut l'interroger. Ce n'est pas un choix de cette
bibliothèque, c'est ainsi que le poêle est conçu.

**N'exposez jamais ce port sur Internet**, et ne le redirigez pas depuis votre box. Laissez le
poêle sur le réseau local, derrière votre routeur.

Pour signaler une faille dans cette bibliothèque, utilisez le
[signalement privé](SECURITY.md) — jamais une issue publique.

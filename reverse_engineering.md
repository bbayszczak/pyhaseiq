# Reverse engineering

## Connexion au poele

On communique avec le poele en websocket non sécurisée sur le port `8080`

## Fonctionnement websocket

Il y a des `pcap` de communication avec le telephone dans plusieurs phases de fonctionnement du poele

- `192.168.1.115`: adresse du client

- `192.168.1.165`: adresse du poele

Une fois la websocket ouverte, on obtient une réponse a chaque message que l'on envoie mais aucun message ne vient du serveur sans que l'on l'ai sollicité: un message envoyé -> un message reçu

dans le `pcap` ./records/arret.json on vois un payload envoyé par le client

```
X3JlcT1hcHBQaGFzZQ==
X3JlcT1hcHBQaGFzZQ==
X3JlcT1hcHBFcnI=
X3JlcT1fb2VtZGV2
X3JlcT1fb2VtdmVy
X3JlcT1fd3ZlcnNpb24=
```

ce qui donne une fois décodé

```
_req=appPhase
_req=appPhase
_req=appErr
_req=_oemdev
_req=_oemver
_req=_wversion
```

aucune idée de pourquoi `_req=appPhase` est présent 2 fois

Il faut je pense identifer toutes les infos pouvant etre requetées

Pour faire cette extraction il faut

1. ouvrir le `pcap` avec Wireshark

2. utiliser ce filtre
```
(ip.src == 192.168.1.165 or ip.dst == 192.168.1.165) and websocket and !(websocket.opcode == 9 or websocket.opcode == 10)
```

3. exporter en JSON `File`>`Export Packet Dissection`>`As JSON`

4. Lancer le script `records/extract.py` avec le path de l'export JSON en parametre

### Requetes / réponses

Toutes les requetes semblent être faites en envoyant une string commencant par `_req=`

| request             | encoded                    | étape(s) | description | réponse |
|---------------------|----------------------------|---|---|---|
| `_req=_l1h`         |                            | 5 | réponse toujours identique, aucune idée du sens | `(?)` |
| `_req=_oemdev`      |                            |  | réponse toujours identique, vu le nom, ça ressemble a un numéro de version | `2` |
| `_req=_oemver`      |                            | 1,2,3,4,5 | réponse toujours identique, semble être un numéro de version | `AAF_5815=9` |
| `_req=_wversion`    |                            | 1,2,3,4,5 | réponse toujours identique, semble être un numéro de version | `1.4` |
| `_req=appAufheiz`   | `X3JlcT1hcHBBdWZoZWl6Cg==` | 2,3 | `Aufheiz` veut dire chauffage en DE, uniquement sur les phases de montée en température, peut etre le pourcentage de montée en temp avant température nominale ? | nombre entre 0 et 100 |
| `_req=appErr`       |                            | 1,2,3,4,5 | réponse toujours identique, pourrait indiquer une erreur dans l'app | `0` |
| `_req=appNach`      |                            | 4 | `Nach` veut dire "après" en Allemand, réponse toujours identique. aucune idée de la signification | `0` |
| `_req=appP`         |`X3JlcT1hcHBQCg==`          | 4 | uniquement pendant température nominale. Pourrait être l'indice de performance ? | int |
| `_req=appP30T[x;x]` |                            | 1,2,3,4,5 | au format `appP30T\[[0-9]+;[0-9]+\]`. Pourrait représenter une demande des mesures x à x sur les 30 dernières mesures. Les valeurs tournent toujours autour de `40` sauf 2/3 exceptions `70`, `9`, `21`, etc... | int |
| `_req=appP30Tx`     |                            | 1,2,3,4,5 | dans toutes les phases, pourrait représenter un nombre de mesures sur les 30 dernières ?  toujours à 30 dans les relevés actuels | `30` |
| `_req=appPhase`     | `X3JlcT1hcHBQaGFzZQo=`     | 1,2,3,4,5 | phase de fonctionnement (voir plus bas) | `[0123]` |
| `_req=appPT[x;x]`   |                            | 2,3,4,5 | au format `appP30T\[[0-9]+;[0-9]+\]`. Pourrait représenter une demande des mesures x à x sur les 30 dernières mesures. | int |
| `_req=appPT[x]`     |                            | 1,2 | 2 occurences seulement, aucune idée de ce que c'est | int |
| `_req=appPTx`       |                            | 1,2,3,4,5 | présent dans toutes les phases, je ne sais pas ce que ça représente | int |
| `_req=appT`         | `X3JlcT1hcHBUCg==`         | 2,3 | semble représenter la température | float |

### appPhase

Le poele peut être dans plusieurs phases différence 

- *appPhase 0*: arret, dans l'attente d'un feu

- *appPhase 1*: montée en température

- *appPhase 2*: température nominale

- *appPhase 3*: besoin de rajouter du bois

- *appPhase 4*: ne plus ajouter de bois

## Utilisation live websocket

`./main.py`

| `_req=`             | description                                                                      |
|---------------------|----------------------------------------------------------------------------------|
| `appAufheiz`        | peut etre le pourcentage de montée en temp avant température nominale ?          |
| `appP`              | uniquement pendant température nominale. Pourrait être l'indice de performance ? |
| `appPhase`          | phase de fonctionnement                                                          |
| `appT`              | semble représenter la température                                                |
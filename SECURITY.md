# Politique de sécurité

## Versions suivies

Le projet est en **alpha** : seule la dernière version publiée reçoit des correctifs.

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique pour une faille de sécurité.**

Utilisez [le signalement privé de GitHub](https://github.com/bbayszczak/pyhaseiq/security/advisories/new),
qui ouvre un canal confidentiel avec les mainteneurs. Une première réponse est visée sous 7 jours.

Merci d'inclure une description du problème, les étapes de reproduction et l'impact estimé.

## Le poêle n'a aucune authentification

Le poêle expose un **WebSocket non chiffré et sans authentification** sur le port `8080` :
toute machine de votre réseau local peut l'interroger. Cette bibliothèque n'y change rien,
elle ne fait que s'y connecter.

**N'exposez jamais ce port sur Internet** et ne le redirigez pas depuis votre box. La seule
protection dont dispose le poêle est de rester sur le réseau local.

Ce point relève de la conception du matériel, pas d'une faille de cette bibliothèque : inutile
de le signaler comme tel.

## Rapports de bug

La bibliothèque étant en lecture seule, ses traces ne contiennent ni identifiant, ni clé, ni
donnée personnelle : une trace `DEBUG` peut être jointe telle quelle à une issue.

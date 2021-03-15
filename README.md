# PI2CChampionshipRunner

Ce serveur permet de faire jouer un tournoi entre plusieurs programme clients. Les clients seront généralement des IAs.

## Déroulement

Les clients doivent d'abord s'inscrire pour se faire connaître du serveur. Dès que deux clients sont inscrits, le serveur commence à faire jouer les matchs.

Chaque participants affrontera tous les autres deux fois, une fois en temps que premier joueur et une fois en temps que deuxième joueur.

Pendant un match, le serveur interroge les joueurs tour à tour pour savoir quel coups ils veulent jouer.

## Communication

Tous les échanges entre le serveur et les clients se font par des communications réseaux TCP en mode texte. Le contenu des messages sera toujours des objects JSON.

Les requêtes contiendront toujours une clé "request" et pourront contenir d'autres clés en fonction de la nature de la requête (voir plus bas).

Les réponses contiendront toujours une clé "response" et pourront également contenir d'autre clés en fonction de la réponse.

## Listes des requêtes / réponse

### Inscriptions

requêtes faite par le client au serveur:

```json
{
   "request": "subscribe",
   "port": 8888,
   "name": "fun_name_for_the_client",
   "matricules": ["12345", "67890"]
}
```

réponse du serveur si tous est ok:

```json
{
   "response": "ok"
}
```

réponse en cas d'erreur:

```json
{
   "response": "error",
   "error": "error message"
}
```

### requête de ping

### requête de coup

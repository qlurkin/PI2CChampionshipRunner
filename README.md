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

## Démarrer le serveur

```shell
python server.py <game_name>
```

Les jeux possibles se trouve dans le répertoire `games`

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

Cette réponse sera suivie, après 1 seconde, d'une requête ping du serveur au port mentionné dans la requête d'inscription.

### requête de ping

Cette requête permet au serveur de vérifier qu'un client est toujours à l'écoute.

La requête faite par le serveur au client est:

```json
{
   "request": "ping"
}
```

Le réponse que le client doit renvoyer est:

```json
{
   "response": "pong"
}
```

Le serveur fera des requête de ping à tous les clients entre chaque match.

### requête de coup

Cette requête permet au serveur de demander à un client quelle coup il joue.

La requête faite par le serveur au client est:

```json
{
   "request": "play",
   "lives": 3,
   "errors": list_of_errors
   "state": state_of_the_game
}
```

La clé `lives` vous indique combien de vies il reste au client. Pour chaque match, les clients ont 3 vies. Il perde une vie à chaque fois qu'il joue un coup invalide. Le client perd le match s'il n'a plus de vies. La clé `errors` contiendra les erreurs qui vous ont fait perdre vos vies.

Le contenu de la clé `state` décrit l'état courant du jeux. Le structure de l'état du jeux dépend du jeux en cours.

La réponse du client est:

```json
{
   "response": "move",
   "move": the_move_played,
   "message": "Fun message"
}
```

s'il veut jouer un coup. La structure du coup dépend du jeu.

La clé `message` est optionnelle.

Le client peut également abandonner avec la réponse:

```json
{
   "response": "giveup",
}
```

Abandonner est parfois nécessaire dans certains jeux lorsque plus aucun coup n'est possible.

La réponse doit généralement être envoyée dans laps de temps précis (3 secondes) sinon elle sera considérée comme un coup invalide et fera perdre une vie.

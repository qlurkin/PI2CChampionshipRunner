# Labyrinthe Game

## The State

Representation of a tile caca

```json
{
  "N": true,
  "E": false,
  "S": true,
  "W": true,
  "item": 1
}
```
The game state:

```json
{
  "players": ["LUR", "HSL"],
  "current": 0,
  "positions": [6, 47],
  "target": 3,
  "remaining": 4,
  "tile": <the free tile>,
  "board": <list of 49 tiles>
}
```
## A Move

```json
  {
    "tile": <the tile in the good orientation>,
    "gate": "A",
    "new_position": 45
  }
```

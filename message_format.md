# Message Format

This document defines the **JSON message formats** exchanged between the **client** and the **server/Game Manager** in a networked Blackjack game.

---

## 1. Game State (`type: "state"`)

**Sent by server** to initialize the game for a player.

```json
{
  "type": "state",
  "player_hand": ["A♠", "10♦"],
  "dealer_card": "8♣"
}
```

| Field         | Type     | Description                           |
|---------------|----------|---------------------------------------|
| `type`        | string   | Always `"state"`                      |
| `player_hand` | string[] | Player’s initial two cards            |
| `dealer_card` | string   | Only the dealer's **first** visible card |

---

## 2. Player Action (`type: "action"`)

**Sent by client** when the player takes an action.

```json
{
  "type": "action",
  "action": "hit"
}
```

| Field     | Type   | Description              |
|-----------|--------|--------------------------|
| `type`    | string | Always `"action"`        |
| `action`  | string | `"hit"` or `"stand"`     |

---

## 3. Update After Hit (`type: "update"`)

**Sent by server** after player chooses `"hit"`.

```json
{
  "type": "update",
  "card": "5♠",
  "new_score": 26,
  "status": "bust"
}
```

| Field        | Type   | Description                              |
|--------------|--------|------------------------------------------|
| `type`       | string | Always `"update"`                        |
| `card`       | string | The card the player just drew            |
| `new_score`  | int    | The player's updated score               |
| `status`     | string | `"ok"` or `"bust"`                       |

---

## 4. Final Result (`type: "result"`)

**Sent by server** when game ends (either by bust or stand).

```json
{
  "type": "result",
  "outcome": "Dealer wins!",
  "dealer_hand": ["8♣", "10♥"]
}
```

| Field         | Type     | Description                       |
|---------------|----------|-----------------------------------|
| `type`        | string   | Always `"result"`                 |
| `outcome`     | string   | Message: `"You win!"` etc.        |
| `dealer_hand` | string[] | The full dealer hand              |

---

## 5. Error (`type: "error"`)

**Sent by server** when an invalid action or message is received.

```json
{
  "type": "error",
  "message": "Invalid action"
}
```

| Field     | Type   | Description                  |
|-----------|--------|------------------------------|
| `type`    | string | Always `"error"`             |
| `message` | string | Description of the problem   |

---

## Notes

- All messages are encoded in **UTF-8 JSON**.
- Card format: `"RankSuit"` — e.g., `"A♠"`, `"10♦"`, `"K♣"`.
- After a `"result"` or `"error"` message, the server may close the connection.
- Clients must handle unexpected or malformed messages gracefully.

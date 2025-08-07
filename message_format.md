# Blackjack Messaging Protocol (Application Layer)

The client communicates with a Blackjack server using a custom **JSON-based application-layer messaging protocol** over **TCP**.

---

## Client-to-Server Messages

### `register`
Sent immediately after establishing a connection to identify the player.

```json
{
  "type": "register",
  "name": "PlayerName"
}
```

---

### `action`
Sent when the player takes an action during their turn.

```json
{
  "type": "action",
  "action": "hit" | "stand"
}
```

---

### `bet`
Sent when the player bets an amount of money.

```json
{
  "type": "bet",
  "amount": 5
}
```

---

## Server-to-Client Messages

### `lobby`
Displays current players in the lobby.

```json
{
  "type": "lobby",
  "all_players": [
    {
      "player_id": "1",
      "player_name": "PlayerName",
      "hand": ["A", "8"],
      "status": "playing",
      "bet": "$10",
      "balance": "$100"
    }
  ]
}
```

---

### `bet_phase`
Indicates that the betting phase is active.

```json
{
  "type": "bet_phase",
  "time": "10",
  "all_players": [...]
}
```

---

### `state`
Initializes a round and sets up hands.

```json
{
  "type": "state",
  "player_id": "1",
  "player_name": "PlayerName",
  "your_hand": ["A", "8"],
  "dealer_card": "Q",
  "all_players": [...]
}
```

---

### `status`
Indicates a player's current status in the game (e.g., `waiting`, `skipped`, `playing`, `stood`, `busted`, `finished`, `disconnected`).

```json
{
  "type": "status",
  "status": "waiting"
}
```

---

### `turn`
Indicates it is a specific player's turn.

```json
{
  "type": "turn",
  "current_player_id": "1",
  "current_player_name": "PlayerName",
  "all_players": [...]
}
```

---

### `update`
Updates a player's hand and state after taking an action.

```json
{
  "type": "update",
  "your_hand": ["A", "8"],
  "card": "2",
  "new_score": 21,
  "status": "ok",
  "dealer_card": "Q",
  "all_players": [...]
}
```

---

### `skipped`
Indicates a player was skipped for not placing a bet within the time limit (10s).

```json
{
  "type": "skipped",
  "player_id": "1",
  "message": "No bet placed; skipped this round.",
  "balance": "100",
  "all_players": [...]
}
```

---

### `round_skipped`
Indicates the round was skipped because no players placed a bet in time.

```json
{
  "type": "round_skipped",
  "message": "No bets were placed. Round skipped.",
  "all_players": [...]
}
```

---

### `result`
Shows the final result of a round (win, lose, push)

```json
{
  "type": "result",
  "outcome": "win",
  "dealer_hand": ["Q", "9"],
  "your_hand": ["A", "K"],
  "balance": "120",
  "bet": 10,
  "player_id": "1",
  "all_players": [...]
}
```

---

### `error`
Indicates a problem with an action or invalid messages.

```json
{
  "type": "error",
  "message": "Invalid action"
}
```

---

## 🔄 Typical Game Flow

```
[Client] → register  
[Server] → lobby  
[Server] → bet_phase  
[Client] → bet  
[Server] → state  
[Server] → turn  
[Client] → action (hit/stand)  
[Server] → update  
     ↻ (loop 6–8 until all players are done)  
[Server] → result  
```

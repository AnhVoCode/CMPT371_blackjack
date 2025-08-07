import socket
import threading
import json
import random
import traceback
import time

HOST = "0.0.0.0"
PORT = 8080

BETTING_TIME = 10  # seconds

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


def make_deck():
    return [rank for rank in RANKS for _ in range(4)]


def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        total += VALUES.get(card, 0)
        if card == 'A':
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def send_json(conn, obj):
    try:
        conn.sendall((json.dumps(obj) + "\n").encode())
    except Exception:
        pass


class PlayerState:
    def __init__(self, conn, addr, pid, name):
        self.conn = conn
        self.addr = addr
        self.id = pid
        self.name = name
        self.hand = []
        self.done = False
        self.status = "waiting"
        self.lock = threading.Lock()
        self.balance = 100
        self.current_bet = 0
        self.active_this_round = False

    def reset_for_round(self):
        self.hand = []
        self.done = False
        self.status = "waiting"
        self.current_bet = 0
        self.active_this_round = False


class SharedGame:
    def __init__(self):
        self.deck = make_deck()
        random.shuffle(self.deck)
        self.deck_lock = threading.Lock()
        self.dealer_hand = []
        self.players = {}
        self.players_lock = threading.Lock()
        self.turn_order = []
        self.current_turn_index = 0
        self.round_lock = threading.Lock()
        self.started = False

    def add_player(self, player: PlayerState):
        with self.players_lock:
            self.players[player.id] = player
        with threading.Lock():
            self.turn_order.append(player.id)

    def remove_player(self, pid):
        with self.players_lock:
            if pid in self.players:
                del self.players[pid]
        if pid in self.turn_order:
            self.turn_order.remove(pid)
            if self.current_turn_index >= len(self.turn_order):
                self.current_turn_index = 0

    def get_player_snapshot(self):
        with self.players_lock:
            return [self.players[p] for p in self.turn_order if p in self.players]

    def deal_initial(self):
        with self.deck_lock:
            active = [p for p in self.get_player_snapshot() if p.active_this_round]
            for player in active:
                player.hand.append(self.deck.pop())
                player.hand.append(self.deck.pop())
                player.status = "playing"
            self.dealer_hand = []
            self.dealer_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())
        self.started = True
        self.current_turn_index = 0

    def player_hit(self, player: PlayerState):
        with self.deck_lock:
            if not self.deck:
                self.deck = make_deck()
                random.shuffle(self.deck)
            card = self.deck.pop()
        player.hand.append(card)
        return card

    def dealer_play(self):
        while hand_value(self.dealer_hand) < 17:
            with self.deck_lock:
                if not self.deck:
                    self.deck = make_deck()
                    random.shuffle(self.deck)
                self.dealer_hand.append(self.deck.pop())

    def all_players_done(self):
        with self.players_lock:
            active = [p for p in self.players.values() if p.active_this_round]
            return all(p.done for p in active)

    def current_player(self):
        for _ in range(len(self.turn_order)):
            pid = self.turn_order[self.current_turn_index % max(1, len(self.turn_order))]
            candidate = self.players.get(pid)
            if candidate and candidate.active_this_round and not candidate.done:
                return candidate
            self.current_turn_index = (self.current_turn_index + 1) % max(1, len(self.turn_order))
        return None


class ServerCore:
    def __init__(self, on_player_update, on_new_connection, on_game_start, on_turn_change, on_round_complete):
        self.game = SharedGame()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(10)
        self.on_player_update = on_player_update
        self.on_new_connection = on_new_connection
        self.on_game_start = on_game_start
        self.on_turn_change = on_turn_change
        self.on_round_complete = on_round_complete
        self._accept_thread = None
        self._running = False
        self._next_pid = 1
        self._in_betting_phase = False
        self._bet_remaining = 0
        self._bet_phase_lock = threading.Lock()

    def start_accepting(self):
        self._running = True
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def shutdown(self):
        self._running = False
        try:
            self.server.close()
        except:
            pass

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self.server.accept()
            except Exception:
                break
            name = None
            try:
                raw = conn.recv(1024).decode()
                msg = json.loads(raw.strip().split("\n")[0])
                if msg.get("type") == "register" and msg.get("name"):
                    name = msg.get("name")
            except Exception:
                pass
            if not name:
                name = f"anon{self._next_pid}"
            pid = f"player{self._next_pid}"
            self._next_pid += 1
            player = PlayerState(conn, addr, pid, name)
            self.game.add_player(player)
            self.on_new_connection(player)
            listener = threading.Thread(target=self._client_listener, args=(player,), daemon=True)
            listener.start()

            # sync new joiner into current phase
            if self._in_betting_phase:
                with self._bet_phase_lock:
                    remaining = self._bet_remaining
                msg = {
                    "type": "bet_phase",
                    "time": remaining,
                    "all_players": [
                        {
                            "player_id": p.id,
                            "player_name": p.name,
                            "bet": p.current_bet,
                            "balance": p.balance,
                            "status": p.status
                        } for p in self.game.get_player_snapshot()
                    ],
                }
                send_json(player.conn, msg)
            elif self.game.started:
                self.broadcast_turn()
            else:
                self.broadcast_lobby()

    def broadcast_lobby(self):
        for player in self.game.get_player_snapshot():
            lobby_msg = {
                "type": "lobby",
                "all_players": [
                    {
                        "player_id": p.id,
                        "player_name": p.name,
                        "hand": p.hand,
                        "status": p.status,
                        "bet": p.current_bet,
                        "balance": p.balance
                    } for p in self.game.get_player_snapshot()
                ],
            }
            send_json(player.conn, lobby_msg)

    def broadcast_bet_phase(self, remaining):
        for player in self.game.get_player_snapshot():
            msg = {
                "type": "bet_phase",
                "time": remaining,
                "all_players": [
                    {
                        "player_id": p.id,
                        "player_name": p.name,
                        "bet": p.current_bet,
                        "balance": p.balance,
                        "status": p.status
                    } for p in self.game.get_player_snapshot()
                ],
            }
            send_json(player.conn, msg)

    def broadcast_turn(self):
        if not self.game.started:
            return
        current = self.game.current_player()
        for player in self.game.get_player_snapshot():
            turn_msg = {
                "type": "turn",
                "current_player_id": current.id if current else None,
                "current_player_name": current.name if current else None,
                "all_players": [
                    {
                        "player_id": p.id,
                        "player_name": p.name,
                        "hand": p.hand,
                        "status": p.status,
                        "bet": p.current_bet,
                        "balance": p.balance
                    } for p in self.game.get_player_snapshot()
                ],
            }
            send_json(player.conn, turn_msg)
        self.on_turn_change(current)

    def send_full_state(self, player: PlayerState):
        msg = {
            "type": "state",
            "player_id": player.id,
            "player_name": player.name,
            "your_hand": player.hand,
            "dealer_card": self.game.dealer_hand[0] if self.game.dealer_hand else None,
            "all_players": [
                {
                    "player_id": p.id,
                    "player_name": p.name,
                    "hand": p.hand,
                    "status": p.status,
                    "bet": p.current_bet,
                    "balance": p.balance
                } for p in self.game.get_player_snapshot()
            ],
        }
        send_json(player.conn, msg)

    def start_game(self):
        if self.game.started or self._in_betting_phase:
            return
        for p in self.game.get_player_snapshot():
            p.reset_for_round()
        self.game.started = False
        self.game.dealer_hand = []

        def betting_sequence():
            with self._bet_phase_lock:
                self._in_betting_phase = True
                self._bet_remaining = BETTING_TIME
            while True:
                with self._bet_phase_lock:
                    remaining = self._bet_remaining
                if remaining <= 0:
                    break
                self.broadcast_bet_phase(remaining)
                time.sleep(1)
                with self._bet_phase_lock:
                    self._bet_remaining -= 1
            with self._bet_phase_lock:
                self._in_betting_phase = False
                self._bet_remaining = 0

            active_players = [p for p in self.game.get_player_snapshot() if p.current_bet > 0]
            if not active_players:
                for player in self.game.get_player_snapshot():
                    skip_msg = {
                        "type": "round_skipped",
                        "message": "No bets were placed. Round skipped.",
                        "all_players": [
                            {
                                "player_id": p.id,
                                "player_name": p.name,
                                "hand": p.hand,
                                "status": p.status,
                                "bet": p.current_bet,
                                "balance": p.balance
                            } for p in self.game.get_player_snapshot()
                        ],
                    }
                    send_json(player.conn, skip_msg)
                self.broadcast_lobby()
                return

            for p in self.game.get_player_snapshot():
                if p.current_bet > 0:
                    p.active_this_round = True
                    p.status = "playing"
                else:
                    p.active_this_round = False
                    p.status = "skipped"

            self.game.deal_initial()
            for player in self.game.get_player_snapshot():
                if not player.active_this_round:
                    skip_msg = {
                        "type": "skipped",
                        "player_id": player.id,
                        "message": "No bet placed; skipped this round.",
                        "balance": player.balance,
                        "all_players": [
                            {
                                "player_id": p.id,
                                "player_name": p.name,
                                "hand": p.hand,
                                "status": p.status,
                                "bet": p.current_bet,
                                "balance": p.balance
                            } for p in self.game.get_player_snapshot()
                        ],
                    }
                    send_json(player.conn, skip_msg)
                else:
                    self.send_full_state(player)
            self.on_game_start(self.game)
            self.broadcast_turn()

        threading.Thread(target=betting_sequence, daemon=True).start()

    def _advance_turn(self):
        for _ in range(len(self.game.turn_order)):
            self.game.current_turn_index = (self.game.current_turn_index + 1) % max(1, len(self.game.turn_order))
            curr = self.game.current_player()
            if curr and curr.active_this_round and not curr.done:
                break

    def _resolve_round(self):
        with self.game.round_lock:
            if not self.game.all_players_done():
                return
            self.game.dealer_play()
            dealer_total = hand_value(self.game.dealer_hand)
            for player in self.game.get_player_snapshot():
                if not player.active_this_round:
                    continue
                player_total = hand_value(player.hand)
                if player_total > 21:
                    outcome = "lose"
                    message = "Busted. Dealer wins."
                    player.balance -= player.current_bet
                else:
                    if dealer_total > 21:
                        outcome = "win"
                        message = "Dealer busted. You win!"
                        player.balance += player.current_bet
                    elif player_total > dealer_total:
                        outcome = "win"
                        message = "You beat the dealer!"
                        player.balance += player.current_bet
                    elif player_total < dealer_total:
                        outcome = "lose"
                        message = "Dealer has higher hand. You lose."
                        player.balance -= player.current_bet
                    else:
                        outcome = "push"
                        message = "Push (tie). Bet returned."
                result = {
                    "type": "result",
                    "outcome": outcome,
                    "message": message,
                    "your_hand": player.hand,
                    "dealer_hand": self.game.dealer_hand,
                    "balance": player.balance,
                    "bet": player.current_bet,
                    "all_players": [
                        {
                            "player_id": p.id,
                            "player_name": p.name,
                            "hand": p.hand,
                            "status": p.status,
                            "bet": p.current_bet,
                            "balance": p.balance
                        } for p in self.game.get_player_snapshot()
                    ],
                }
                send_json(player.conn, result)
                player.status = "finished"
            self.on_round_complete(self.game)
            self.game.started = False
            time.sleep(3)  # allow clients to show result
            self.broadcast_lobby()

    def _client_listener(self, player: PlayerState):
        conn = player.conn
        try:
            while True:
                data = conn.recv(2048).decode()
                if not data:
                    break
                for line in data.strip().splitlines():
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        send_json(conn, {"type": "error", "message": "Invalid JSON."})
                        continue

                    if msg.get("type") == "bet":
                        # only allow bets during the betting phase
                        if not self._in_betting_phase:
                            send_json(player.conn, {"type": "error", "message": "Betting is closed. Wait for next round."})
                            continue
                        amount = msg.get("amount", 0)
                        with player.lock:
                            if amount <= 0 or amount > player.balance:
                                send_json(player.conn, {"type": "error", "message": "Invalid bet amount."})
                            else:
                                player.current_bet = amount
                        with self._bet_phase_lock:
                            remaining = self._bet_remaining
                        self.broadcast_bet_phase(remaining if self._in_betting_phase else 0)
                        continue

                    if msg.get("type") == "action":
                        action = msg.get("action", "").lower()
                        if player.done:
                            send_json(conn, {"type": "error", "message": "Already done."})
                            continue
                        current = self.game.current_player()
                        if not current or current.id != player.id:
                            send_json(conn, {"type": "error", "message": "Not your turn."})
                            continue

                        if action == "hit":
                            advance = False
                            with player.lock:
                                card = self.game.player_hit(player)
                                new_score = hand_value(player.hand)
                                update = {
                                    "type": "update",
                                    "player_id": player.id,
                                    "player_name": player.name,
                                    "card": card,
                                    "new_score": new_score,
                                    "status": "bust" if new_score > 21 else "ok",
                                    "your_hand": player.hand,
                                    "all_players": [
                                        {
                                            "player_id": p.id,
                                            "player_name": p.name,
                                            "hand": p.hand,
                                            "status": p.status,
                                            "bet": p.current_bet,
                                            "balance": p.balance
                                        } for p in self.game.get_player_snapshot()
                                    ],
                                }
                                send_json(conn, update)
                                if new_score > 21:
                                    player.done = True
                                    player.status = "busted"
                                    advance = True
                            self.on_player_update(player)
                            if self.game.all_players_done():
                                self._resolve_round()
                            else:
                                if advance:
                                    self._advance_turn()
                                self.broadcast_turn()

                        elif action == "stand":
                            with player.lock:
                                player.done = True
                                player.status = "stood"
                            send_json(conn, {
                                "type": "update",
                                "player_id": player.id,
                                "player_name": player.name,
                                "action": "stand",
                                "all_players": [
                                    {
                                        "player_id": p.id,
                                        "player_name": p.name,
                                        "hand": p.hand,
                                        "status": p.status,
                                        "bet": p.current_bet,
                                        "balance": p.balance
                                    } for p in self.game.get_player_snapshot()
                                ],
                            })
                            self.on_player_update(player)
                            if self.game.all_players_done():
                                self._resolve_round()
                            else:
                                self._advance_turn()
                                self.broadcast_turn()
                        else:
                            send_json(conn, {"type": "error", "message": f"Unknown action '{action}'."})
        except Exception:
            traceback.print_exc()
        finally:
            self.game.remove_player(player.id)
            player.status = "disconnected"
            self.on_player_update(player)
            try:
                conn.close()
            except:
                pass

import random
import threading
from player_state import PlayerState

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

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
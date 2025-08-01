import random
from player import Player

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']


class Game_Manager:
    def __init__(self):
        self.deck = []
        self.setup_deck()
        self.players = []
        self.player_count = 0
        self.add_player() #add dealer
        self.dealer = self.players[0]
          
    def setup_deck(self):
        self.deck.clear()
        for rank in RANKS:
            for suit in SUITS:
                card = rank + suit
                self.deck.append(card)
        
        random.shuffle(self.deck)
    
    def add_player(self):
        player = Player(self.player_count)
        self.player_count += 1
        self.deal_card(player, 2)
        self.players.append(player)
        
    def deal_card(self, player, number_of_cards):
        for i in range(number_of_cards):
            card = self.deck.pop()
            player.add_card(card)
            
    def play_dealer_turn(self):
        while self.dealer.score < 17:
            self.deal_card(self.dealer, 1)
    
    def reset_game(self):
        self.setup_deck()
        for player in self.players:
            player.reset()
            self.deal_card(player, 2)
            
    def get_player_from_playerID(self, playerID):
        for player in self.players:
            if player.playerID == playerID:
                return player
        return None
            
    def get_dealer_hand(self):
        return self.dealer.hand
    
    def get_player_hand(self, playerID):
        player = self.get_player_from_playerID(playerID)
        return player.hand
        
        
    
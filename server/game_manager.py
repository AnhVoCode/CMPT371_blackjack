import random
from player import Player

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']


class Game_Manager:
    def __init__(self):
        self.deck = []
        self.players = []
        self.player_count = 0
        self.add_player() #Dealer
        self.dealer = self.players[0]
        
        self.active_players = []
          
    #Handle events
    def start_game(self):
        self.setup_deck()
        
        game_info = []
        for player in self.players:
            self.active_players.append(player)
            self.deal_card(player.playerID, 2)
            game_info.append((player.playerID, player.hand, player.score))
        return game_info
    
    def reset_game(self):
        self.setup_deck()
        self.current_turn_index = 1
        for player in self.players:
            player.reset()
            self.deal_card(player.playerID, 2)
    
    def handle_hit(self, playerID):
        player = self.players[playerID]
        card = self.deal_card(player.playerID, 1)
        if player.is_bust:
            self.handle_stand()
        return [card, player.score, player.is_bust]
    
    #def handle_stand(self): 
    #def handle_result(self): return [outcome, self.dealer.hand]
        
    #Gameplay
    def add_player(self):
        player = Player(self.player_count)
        self.player_count += 1
        self.players.append(player)
        return player
        
    def deal_card(self, playerID, number_of_cards):
        player = self.get_player_from_playerID(playerID)
        if not player:
            return "No Player Found"
        
        card = ""
        while number_of_cards > 0:
            card = self.deck.pop()
            player.add_card(card)
            number_of_cards -= 1
        return card
            
    def play_dealer_turn(self):
        while self.dealer.score < 17:
            self.deal_card(self.dealer.playerID, 1)
        
    #Helpers
    def get_player_from_playerID(self, playerID):
        for player in self.players:
            if player.playerID == playerID:
                return player
        return None
    
    def delete_player(self, playerID):
        player = self.get_player_from_playerID(playerID)
        if player:
            self.players.remove(player)
            self.player_count -= 1
            return True
        return False
    
    def setup_deck(self):
        self.deck.clear()
        for rank in RANKS:
            for suit in SUITS:
                card = rank + suit
                self.deck.append(card)
        
        random.shuffle(self.deck)
        
    
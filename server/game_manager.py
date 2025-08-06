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
        self.add_player() #Dealer
        self.dealer = self.players[0]
        self.current_turn_index = 1
          
    def setup_deck(self):
        self.deck.clear()
        for rank in RANKS:
            for suit in SUITS:
                card = rank + suit
                self.deck.append(card)
        
        random.shuffle(self.deck)
    
    #Handle events
    def handle_new_player(self):
        player = self.add_player()
        return [player.hand, self.dealer.hand[0]]
    
    def handle_hit(self):
        player = self.players[self.current_turn_index]
        card = self.deal_card(player.playerID, 1)
        if player.is_bust:
            self.handle_stand()
        return [card, player.score, player.is_bust]
    
    def handle_stand(self): 
        self.current_turn_index += 1
        if self.current_turn_index > self.player_count - 1:
            self.current_turn_index = 0

    # Returns a dictionary: {playerID: outcome, playerID: outcome, ...}
    # Does not include dealer
    def handle_result(self):
        results = {}
        for i in range(self.player_count - 1):
            current_player = self.players[i+1]
            if current_player.is_bust:
                outcome = "You lose!" 
            else:
                if self.dealer.is_bust:
                    outcome = "You win!"
                else:
                    if current_player.is_blackjack:
                        if self.dealer.is_blackjack:
                            outcome = "Push!"
                        else:
                            outcome = "You win!"
                    else:
                        if self.dealer.is_blackjack or self.dealer.score > current_player.score:
                            outcome = "You lose!"
                        elif self.dealer.score == current_player.score:
                            outcome = "Push!"
                        else:
                            outcome = "You win!"
            results[current_player.playerID] = outcome

        return results
        
    #Gameplay
    def add_player(self):
        player = Player(self.player_count)
        self.player_count += 1
        self.players.append(player)
        self.deal_card(player.playerID, 2)
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
    
    def reset_game(self):
        self.setup_deck()
        self.current_turn_index = 1
        for player in self.players:
            player.reset()
            self.deal_card(player.playerID, 2)
        
    #Helpers
    def get_player_from_playerID(self, playerID):
        for player in self.players:
            if player.playerID == playerID:
                return player
        return None
        
    
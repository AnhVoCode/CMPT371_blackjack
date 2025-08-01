class Player:
    def __init__(self, playerID):
        self.playerID = playerID
        self.hand = []
        self.score = 0
        self.is_bust = False
        self.is_blackjack = False
    
    def add_card(self, card):
        self.hand.append(card)
        
        card_rank = card[:-1]
        if card_rank in ['J', 'Q', 'K']:
            self.score += 10
        elif card_rank == 'A':
            if (self.score + 11) > 21:
                self.score += 1
            else:
                self.score += 11
        else:
            self.score += int(card_rank)
            
        self.update_state()
    
    def update_state(self):
        if self.score == 21 and len(self.hand) == 2:
            self.is_blackjack = True
        elif self.score > 21:
            self.is_bust = True
    
    def reset(self):
        self.hand.clear()
        self.score = 0
        self.is_bust = False
        self.is_blackjack = False
        
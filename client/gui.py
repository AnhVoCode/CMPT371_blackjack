#  Blackjack User Interface

import tkinter as tk

class BlackjackGUI:
    def __init__(self, send_callback):
        self.send_callback = send_callback

        self.window = tk.Tk()
        self.window.title("Blackjack")

        # Dealer and player hands
        self.dealer_label = tk.Label(self.window, text="Dealer:  ", font=("Arial", 14))
        self.dealer_label.pack(pady=10)

        self.player_label = tk.Label(self.window, text="You:  ", font=("Arial", 14))
        self.player_label.pack(pady=10)

        # Game status (turn info / result)
        self.status_label = tk.Label(self.window, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack(pady=10)

        # Action buttons
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=5)

        self.hit_button = tk.Button(self.button_frame, text="Hit", width=10, command=lambda: self.send_action("hit"))
        self.hit_button.pack(side=tk.LEFT, padx=5)
        
        self.stand_button = tk.Button(self.button_frame, text="Stand", width=10, command=lambda: self.send_action("stand"))
        self.stand_button.pack(side=tk.RIGHT, padx=5)

    def send_action(self, action):
        """
        Sends the player's action ("hit" or "stand") to the server
        and logs the action in the GUI.
        """
        self.set_status(f"You chose: {action}")
        self.send_callback(action)
        self.disable_buttons()
    
    def update_state(self, player_hand, dealer_card):
        """
        Updates the GUI to display the player's current hand
        and the dealer's visible card.
        """
        self.player_label.config(text=f"You: {' '.join(player_hand)}")
        self.dealer_label.config(text=f"Dealer shows: {dealer_card}")
    
    def update_result(self, outcome, dealer_hand):
        """
        Displays the final outcome of the game and shows
        the dealer's full hand.
        """
        self.dealer_label.config(text=f"Dealer: {' '.join(dealer_hand)}")
        self.set_status(outcome)
        self.disable_buttons()
    
    def set_status(self, message):
        """Update the status/info label (e.g., your turn, result)."""
        self.status_label.config(text=message)
    
    def enable_buttons(self):
        """Enable Hit and Stand buttons."""
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)

    def disable_buttons(self):
        """Disable Hit and Stand buttons (e.g., not the player's turn)."""
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
    
    def run(self):
        self.window.mainloop()


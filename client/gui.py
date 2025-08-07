import tkinter as tk

class BlackjackGUI:
    def __init__(self, send_callback):
        self.send_callback = send_callback
        self.betting_enabled = False  # internal guard

        self.window = tk.Tk()
        self.window.title("Blackjack")

        self.dealer_label = tk.Label(self.window, text="Dealer shows: ?", font=("Arial", 14))
        self.dealer_label.pack(pady=5)

        self.player_label = tk.Label(self.window, text="You: ", font=("Arial", 14))
        self.player_label.pack(pady=5)

        self.bet_frame = tk.Frame(self.window)
        self.bet_frame.pack(pady=5)
        tk.Label(self.bet_frame, text="Balance:").grid(row=0, column=0)
        self.balance_label = tk.Label(self.bet_frame, text="$100")
        self.balance_label.grid(row=0, column=1, padx=5)
        tk.Label(self.bet_frame, text="Your Bet:").grid(row=1, column=0)
        self.bet_label = tk.Label(self.bet_frame, text="$0")
        self.bet_label.grid(row=1, column=1, padx=5)

        tk.Label(self.bet_frame, text="Chips:").grid(row=2, column=0, sticky="w")
        self.current_bet_value = 0
        self.chip_values = [1, 5, 10, 20]
        self.chip_buttons = {}
        for i, val in enumerate(self.chip_values):
            b = tk.Button(self.bet_frame, text=f"${val}", command=lambda v=val: self.add_chip(v))
            b.grid(row=2, column=1 + i, padx=2)
            self.chip_buttons[val] = b
        self.clear_button = tk.Button(self.bet_frame, text="Clear", command=self.clear_bet)
        self.clear_button.grid(row=3, column=0, pady=4)
        self.place_button = tk.Button(self.bet_frame, text="Place Bet", command=self.place_bet)
        self.place_button.grid(row=3, column=1, pady=4)

        self.other_label = tk.Label(self.window, text="Other players:", font=("Arial", 12, "underline"))
        self.other_label.pack(pady=(10, 0))
        self.other_text = tk.Label(self.window, text="", font=("Consolas", 10), justify=tk.LEFT)
        self.other_text.pack(pady=2)

        self.status_label = tk.Label(self.window, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack(pady=5)

        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=5)

        self.hit_button = tk.Button(self.button_frame, text="Hit", width=10, command=lambda: self.send_callback("hit"))
        self.hit_button.pack(side=tk.LEFT, padx=5)
        self.stand_button = tk.Button(self.button_frame, text="Stand", width=10, command=lambda: self.send_callback("stand"))
        self.stand_button.pack(side=tk.LEFT, padx=5)

        self.disable_buttons()
        self.disable_betting()

    def add_chip(self, val):
        if not self.betting_enabled:
            return
        bal = int(self.balance_label.cget("text").strip("$"))
        if self.current_bet_value + val > bal:
            return
        self.current_bet_value += val
        self.bet_label.config(text=f"${self.current_bet_value}")
        self.update_chip_states()

    def clear_bet(self):
        if not self.betting_enabled:
            return
        self.current_bet_value = 0
        self.bet_label.config(text="$0")
        self.update_chip_states()

    def place_bet(self):
        if not self.betting_enabled:
            return
        self.send_callback({"type": "bet", "amount": self.current_bet_value})

    def update_you(self, name, player_hand):
        self.player_label.config(text=f"You ({name}): {' '.join(player_hand)}")

    def update_state(self, _, dealer_card):
        if dealer_card and dealer_card != "None":
            self.dealer_label.config(text=f"Dealer shows: {dealer_card}")
        else:
            self.dealer_label.config(text="Dealer shows: ?")

    def update_result(self, outcome, dealer_hand):
        self.dealer_label.config(text=f"Dealer: {' '.join(dealer_hand)}")

    def set_status(self, message, color="blue"):
        self.status_label.config(text=message, fg=color)

    def set_other_players_text(self, text):
        self.other_text.config(text=text)

    def set_balance(self, amount):
        self.balance_label.config(text=f"${amount}")
        self.update_chip_states()

    def set_bet(self, amount):
        self.current_bet_value = amount
        self.bet_label.config(text=f"${amount}")
        self.update_chip_states()

    def update_chip_states(self):
        bal = int(self.balance_label.cget("text").strip("$"))
        for val, btn in self.chip_buttons.items():
            if not self.betting_enabled or self.current_bet_value + val > bal:
                btn.config(state=tk.DISABLED)
            else:
                btn.config(state=tk.NORMAL)

    def enable_buttons(self):
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)

    def disable_buttons(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

    def enable_betting(self):
        self.betting_enabled = True
        for btn in self.chip_buttons.values():
            btn.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
        self.place_button.config(state=tk.NORMAL)
        self.update_chip_states()

    def disable_betting(self):
        self.betting_enabled = False
        for btn in self.chip_buttons.values():
            btn.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.place_button.config(state=tk.DISABLED)

    def clear_hand_display(self):
        self.player_label.config(text="You: ")
        self.dealer_label.config(text="Dealer shows: ?")

    def run(self):
        self.window.mainloop()

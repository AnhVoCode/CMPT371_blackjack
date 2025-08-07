import tkinter as tk
from tkinter import ttk
from server import ServerCore

class ServerGUI:
    def __init__(self):
        self.core = ServerCore(
            on_player_update=self.on_player_update,
            on_new_connection=self.on_new_connection,
            on_game_start=self.on_game_start,
            on_turn_change=self.on_turn_change,
            on_round_complete=self.on_round_complete,
        )
        self.root = tk.Tk()
        self.root.title("Blackjack Server Manager")

        self.tree = ttk.Treeview(self.root, columns=("name", "addr", "status", "bet", "balance"), show="headings")
        self.tree.heading("name", text="Name")
        self.tree.heading("addr", text="Address")
        self.tree.heading("status", text="Status")
        self.tree.heading("bet", text="Bet")
        self.tree.heading("balance", text="Balance")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.lobby_label = tk.Label(self.root, text="Players: 0")
        self.lobby_label.pack(pady=2)
        self.status_label = tk.Label(self.root, text="Waiting for Start Game.")
        self.status_label.pack(pady=2)
        self.turn_label = tk.Label(self.root, text="Current turn: -")
        self.turn_label.pack(pady=2)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        self.start_btn = tk.Button(btn_frame, text="Start Game", command=self.start_game)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.kill_btn = tk.Button(btn_frame, text="Kill Server", command=self.shutdown)
        self.kill_btn.pack(side=tk.LEFT, padx=5)

        self.dealer_label = tk.Label(self.root, text="Dealer: (hidden until resolution)")
        self.dealer_label.pack(pady=5)

        self.core.start_accepting()
        self.refresh_loop()

    def refresh_loop(self):
        current = self.core.game.get_player_snapshot()
        self.lobby_label.config(text=f"Players: {len(current)}")
        existing = set(self.tree.get_children())
        for p in current:
            display_addr = f"{p.addr[0]}:{p.addr[1]}"
            bet = f"${p.current_bet}"
            balance = f"${p.balance}"
            if p.id in existing:
                self.tree.item(p.id, values=(p.name, display_addr, p.status, bet, balance))
                existing.remove(p.id)
            else:
                self.tree.insert("", tk.END, iid=p.id, values=(p.name, display_addr, p.status, bet, balance))
        for stale in existing:
            self.tree.delete(stale)
        self.root.after(200, self.refresh_loop)

    def on_new_connection(self, player):
        self.status_label.config(text=f"{player.name} connected.")

    def on_player_update(self, player):
        pass

    def on_game_start(self, game):
        self.dealer_label.config(text=f"Dealer shows: {game.dealer_hand[0]}")
        self.status_label.config(text="Betting done. Game started.")

    def on_turn_change(self, current_player):
        if current_player:
            self.turn_label.config(text=f"Current turn: {current_player.name}")
        else:
            self.turn_label.config(text="Current turn: -")

    def on_round_complete(self, game):
        self.dealer_label.config(text=f"Dealer final hand: {' '.join(game.dealer_hand)}")
        self.status_label.config(text="Round complete.")

    def start_game(self):
        self.core.start_game()

    def shutdown(self):
        self.core.shutdown()
        self.root.quit()

    def run(self):
        self.root.mainloop()

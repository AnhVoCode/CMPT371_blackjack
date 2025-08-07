import socket
import threading
import sys
import json
import tkinter as tk
from gui import BlackjackGUI

import time

VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

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

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

# Name prompt dialog
name_prompt = tk.Tk()
name_prompt.title("Enter Name")
name_var = tk.StringVar(value="Player")
tk.Label(name_prompt, text="Name:").pack(side=tk.LEFT, padx=5, pady=5)
entry = tk.Entry(name_prompt, textvariable=name_var)
entry.pack(side=tk.LEFT, padx=5, pady=5)
submitted = threading.Event()

def submit_name():
    submitted.set()
    name_prompt.destroy()

tk.Button(name_prompt, text="OK", command=submit_name).pack(side=tk.LEFT, padx=5)
name_prompt.mainloop()
submitted.wait()
name = name_var.get().strip() or "Anonymous"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((SERVER_IP, PORT))
except Exception as e:
    print(f"Failed to connect to {SERVER_IP}:{PORT} -> {e}")
    sys.exit(1)

# register
reg = {"type": "register", "name": name}
sock.sendall((json.dumps(reg) + "\n").encode())

player_id = None
own_name = None
game_over = False

# suppression window so lobby updates don't immediately stomp result
suppress_lobby_until = 0.0

def send_action(obj):
    if isinstance(obj, dict):
        msg = obj
    else:
        msg = {"type": "action", "action": obj}
    try:
        sock.sendall((json.dumps(msg) + "\n").encode())
    except Exception as e:
        gui.set_status(f"Send failed: {e}", color="red")

def format_other_players(all_players, self_id):
    lines = []
    for p in all_players:
        label = f"{p.get('player_name')} ({p.get('player_id')}):"
        hand = " ".join(p.get("hand", []))
        status = p.get("status", "")
        bet = p.get("bet", 0)
        balance = p.get("balance", 0)
        lines.append(f"{label} {hand} [{status}] Bet:${bet} Bal:${balance}")
    return "\n".join(lines) if lines else "No other players."

def receive_messages():
    global player_id, own_name, game_over, suppress_lobby_until
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                gui.set_status("Disconnected", color="red")
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    gui.set_status("Malformed message", color="red")
                    continue

                mtype = msg.get("type")
                if mtype == "lobby":
                    all_players = msg.get("all_players", [])
                    gui.set_other_players_text(format_other_players(all_players, player_id or ""))
                    if time.time() > suppress_lobby_until:
                        gui.set_status("Waiting for server to start...", color="black")
                    for p in all_players:
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                    gui.disable_betting()

                elif mtype == "bet_phase":
                    all_players = msg.get("all_players", [])
                    remaining = msg.get("time", 0)
                    gui.set_status(f"Place your bet! {remaining}s", color="purple")
                    gui.set_other_players_text(format_other_players(all_players, player_id or ""))
                    for p in all_players:
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                    gui.enable_betting()

                elif mtype == "state":
                    player_id = msg.get("player_id")
                    own_name = msg.get("player_name", own_name)
                    your_hand = msg.get("your_hand", [])
                    dealer_card = msg.get("dealer_card") or "?"
                    gui.update_you(own_name, your_hand)
                    gui.update_state([], dealer_card)
                    gui.set_status("Waiting for your turn.", color="black")
                    gui.disable_buttons()
                    gui.disable_betting()
                    gui.set_other_players_text(format_other_players(msg.get("all_players", []), player_id))
                    for p in msg.get("all_players", []):
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                            gui.set_bet(p.get("bet", 0))

                elif mtype == "turn":
                    current_id = msg.get("current_player_id")
                    current_name = msg.get("current_player_name")
                    all_players = msg.get("all_players", [])
                    gui.set_other_players_text(format_other_players(all_players, player_id))
                    if current_id == player_id:
                        gui.set_status("Your turn.", color="green")
                        gui.enable_buttons()
                    else:
                        gui.set_status(f"Waiting for {current_name} to finish.", color="blue")
                        gui.disable_buttons()
                    gui.disable_betting()
                    for p in all_players:
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                            gui.set_bet(p.get("bet", 0))

                elif mtype == "update":
                    your_hand = msg.get("your_hand", [])
                    dealer_card = msg.get("dealer_card")
                    if dealer_card:
                        gui.update_state([], dealer_card)
                    gui.update_you(own_name or msg.get("player_name", ""), your_hand)
                    status = msg.get("status", "")
                    if status == "bust":
                        gui.set_status("BUSTED! Waiting for round resolution...", color="red")
                        gui.disable_buttons()
                    elif msg.get("action") == "stand":
                        gui.set_status("You stood. Waiting for others...", color="purple")
                        gui.disable_buttons()
                    else:
                        card = msg.get("card")
                        new_score = msg.get("new_score")
                        if card is not None and new_score is not None:
                            gui.set_status(f"Got card: {card}. Score: {new_score}", color="black")
                    gui.disable_betting()
                    gui.set_other_players_text(format_other_players(msg.get("all_players", []), msg.get("player_id")))
                    for p in msg.get("all_players", []):
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                            gui.set_bet(p.get("bet", 0))

                elif mtype == "skipped":
                    gui.set_status(msg.get("message", ""), color="gray")
                    gui.set_other_players_text(format_other_players(msg.get("all_players", []), msg.get("player_id")))
                    gui.set_balance(msg.get("balance", 0))
                    gui.disable_betting()

                elif mtype == "round_skipped":
                    gui.set_status(msg.get("message", ""), color="orange")
                    gui.set_other_players_text(format_other_players(msg.get("all_players", []), player_id))
                    for p in msg.get("all_players", []):
                        if p.get("player_id") == player_id:
                            gui.set_balance(p.get("balance", 0))
                            gui.set_bet(0)
                    gui.disable_buttons()
                    gui.disable_betting()

                elif mtype == "result":
                    outcome = msg.get("outcome")
                    dealer_hand = msg.get("dealer_hand", [])
                    your_hand = msg.get("your_hand", [])
                    all_players = msg.get("all_players", [])
                    bet = msg.get("bet", 0)
                    balance = msg.get("balance", 0)

                    gui.update_result(outcome, dealer_hand)
                    gui.update_you(own_name or msg.get("player_name", ""), your_hand)
                    gui.set_other_players_text(format_other_players(all_players, msg.get("player_id")))

                    if outcome == "win":
                        gui.set_status(f"YOU WON! +${bet}", color="green")
                    elif outcome == "lose":
                        gui.set_status(f"YOU LOST! -${bet}", color="red")
                    else:
                        gui.set_status("PUSH (tie). Bet returned.", color="orange")

                    if balance is not None:
                        gui.set_balance(balance)

                    gui.disable_buttons()
                    gui.disable_betting()
                    game_over = True

                    suppress_lobby_until = time.time() + 3.5

                    def reset_to_lobby():
                        time.sleep(3)
                        gui.clear_hand_display()
                        gui.set_bet(0)
                        gui.set_status("Waiting for server to start...", color="black")
                    threading.Thread(target=reset_to_lobby, daemon=True).start()

                elif mtype == "error":
                    gui.set_status("Error: " + msg.get("message", ""), color="red")

        except Exception as e:
            gui.set_status(f"Receive error: {e}", color="red")
            break

def send_action_to_server(action):
    send_action(action)

# launch GUI
gui = BlackjackGUI(send_action_to_server)
gui.set_status("Connecting...", color="gray")

receiver_thread = threading.Thread(target=receive_messages, daemon=True)
receiver_thread.start()

gui.run()

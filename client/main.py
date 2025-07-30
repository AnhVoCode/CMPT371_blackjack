# Blackjack Client (Players)
# Responsibilities:
# - Connect to server using IP and port
# - Send actions ("hit", "stand")
# - Receive updates and display game state

import socket
import threading
import sys
import json
from gui import BlackjackGUI

# -------------------- Configuration ----------------------
SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'       # Localhost
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8080              # Default Port #


# # ----------------- TCP Client Socket --------------------
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((SERVER_IP, PORT))
    print(f"[Connected] to server at {SERVER_IP}:{PORT}")
except Exception as e:
    print(f"[Error] Connection failed: {e}")
    sys.exit()


# ------------------  Send Action to Server ----------------------
def send_action_to_server(action):
    try:
        action_json = json.dumps({
            "type": "action",
            "action": action
        })
        client_socket.sendall(action_json.encode())
        gui.set_status(f"You chose: {action}")
        gui.disable_buttons()
    except Exception as e:
        gui.set_status(f"[Error] sending action: {e}")



# --------------- Handle Messages from Server ----------------------
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                gui.set_status("Disconnected: Server closed the connection.")
                break
            # Raw message for debugging
            # gui.add_log(f"[Server]: {message}")

            # Parse structured JSON messages
            try:
                data = json.loads(message)
                
                if data["type"] == "state":
                    gui.update_state(data["player_hand"], data["dealer_card"])
                    gui.set_status("Your turn, choose Hit or Stand")
                    gui.enable_buttons()
                
                elif data["type"] == "update":
                    gui.set_status(f"You drew: {data['card']}  (Score: {data['new_score']})")
                    if data["status"] == "bust":
                        gui.set_status("You busted!")
                        gui.disable_buttons()
                
                elif data["type"] == "result":
                    gui.update_result(data["outcome"], data["dealer_hand"])
                
                elif data["type"] == "error":
                    gui.set_status(f"[Error] {data['message']}")
                    gui.disable_buttons()
                    
            except json.JSONDecodeError:
                # Fallback: handle basic string messages
                if "Your turn" in message or "Choose action" in message:
                    gui.set_status("Your turn. Choose Hit or Stand")
                    gui.enable_buttons()

        except Exception as e:
            gui.set_status(f"[Error receiving message] {e}")
            break





# --------------------- Launch GUI -------------------------
gui = BlackjackGUI(send_action_to_server)
gui.set_status("Connected to server")

# Start background thread to receive server messages
receiver_thread = threading.Thread(target=receive_messages, daemon=True)
receiver_thread.start()

# Start the GUI loop
gui.run()

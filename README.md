# CMPT 371 Summer 2025 – Multiplayer Blackjack Game

This repository contains the source code and documentation for a multiplayer Blackjack game developed as part of the **CMPT 371 Summer 2025** course project. The game is implemented using **Python socket programming** and follows a **client-server architecture**, where multiple clients connect remotely to a host server to participate in a game of Blackjack.

---

## Project Overview

- **Game**: Multiplayer Blackjack
- **Architecture**: Client-server
- **Language**: Python 3
- **Networking**: TCP sockets (no third-party networking libraries)
- **Concurrency Control**: Shared object access synchronized via custom locking logic

### Prerequisites

- **Python** ≥ 3.8  
- **pip**  
- **Git**  

> _On Windows, you’ll need Git Bash or WSL for the build script._

### Setup & Installation

1. **Clone the repository**
   
   ```bash
   git clone https://github.com/AnhVoCode/CMPT371_blackjack.git
   cd CMPT371_blackjack
3. **Running the server**
   
   ```bash
   cd server
   python -c "from server_gui import ServerGUI; ServerGUI().run()"

  > _Listens on 0.0.0.0:8080 by default_

  > _Opens a simple GUI for monitoring connected clients_
3. **Running the client**

   ```bash
   cd client
   python main.py <SERVER_IP> 8080 ```````

  > _Replace <SERVER_IP> with the server’s LAN or public IP_

  > _Defaults to 127.0.0.1 if omitted_


---

## 🎉 Thank You!

Thank you for taking the time to explore this repository.

If you have any questions or run into problems, please reach out to any of our team members.



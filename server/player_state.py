import threading

class PlayerState:
    def __init__(self, conn, addr, pid, name):
        self.conn = conn
        self.addr = addr
        self.id = pid
        self.name = name
        self.hand = []
        self.done = False
        self.status = "waiting"
        self.lock = threading.Lock()
        self.balance = 100
        self.current_bet = 0
        self.active_this_round = False

    def reset_for_round(self):
        self.hand = []
        self.done = False
        self.status = "waiting"
        self.current_bet = 0
        self.active_this_round = False
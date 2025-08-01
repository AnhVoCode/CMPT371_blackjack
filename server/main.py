from game_manager import Game_Manager

#For debugging purposes only
def main():
    game = Game_Manager()
    
    #game setup
    game.handle_new_player()
    for i in range(game.player_count):
        p = game.players[i]
        if i == 0:
            print(f"dealer: {p.hand} with score {p.score}")
        else:
            print(f"player {p.playerID}: {p.hand} with score {p.score}")
    
    #game simulation (player hit + dealer)
    game.deal_card(1, 1)
    print(f"player {game.players[1].playerID}: {game.players[1].hand} with score {game.players[1].score}")
    game.play_dealer_turn()
    print(f"dealer: {game.players[0].hand} with score {game.players[0].score}")
    
    #incorrect ID given
    if game.deal_card(11, 1):
        print("\nERROR")
    else:
        print("\nSUCCESS")
    
    #reset game
    print("\nRESET")
    game.reset_game()
    print(f"dealer: {game.players[0].hand} with score {game.players[0].score}")
    print(f"player {game.players[1].playerID}: {game.players[1].hand} with score {game.players[1].score}")
    
    
if __name__ == "__main__":
    main()

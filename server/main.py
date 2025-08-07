from game_manager import Game_Manager

#For debugging purposes only
def main():
    game = Game_Manager()
    
    #game setup
    game.add_player()
    game_info = game.start_game()
    
    for i, player_info in enumerate(game_info):
        if i == 0:
            print(f"dealer: {player_info[1]} with score {player_info[2]}")
        else:
            print(f"player {player_info[0]}: {player_info[1]} with score {player_info[2]}")
    
    #game simulation (player hit + dealer)
    game.handle_hit(1)
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
    
    print(f"\nplayer count: {game.player_count}, players: {[p.playerID for p in game.players]}")
    game.delete_player(game.players[1].playerID)
    print(f"player count: {game.player_count}, players: {[p.playerID for p in game.players]}")
    
    
if __name__ == "__main__":
    main()

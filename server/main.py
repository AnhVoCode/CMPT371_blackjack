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

    # Simulate game with 3 players + dealer
    game.handle_new_player()
    game.handle_new_player()

    while(game.current_turn_index != 0):
        current_player = game.players[game.current_turn_index]
        current_playerID = current_player.playerID
        print(f"\nPlayer {current_playerID}:")
        print(f"Current hand: {current_player.hand}\nScore: {current_player.score}")
        print("Enter action (hit/stand): ")
        action = input()

        if action == "hit":
            game.handle_hit()
            print(f"New hand: {current_player.hand}\nScore: {current_player.score}")
        elif action == "stand":
            game.handle_stand()
        else:
            print("Invalid action")

    game.play_dealer_turn()
    results = game.handle_result()
    print("\nResults:")
    for player, outcome in results.items():
        print(f"player {player}: {outcome} {game.get_player_from_playerID(player).hand} with score {game.get_player_from_playerID(player).score}")
    print(f"Dealer: {game.players[0].hand} with score {game.players[0].score}")

    # Reset game and check if current_turn_index is properly reset
    game.reset_game()
    print("\nRESET")
    current_player = game.players[game.current_turn_index]
    print(f"current player: {current_player.hand} with score {current_player.score}")
    print(f"player {game.players[1].playerID}: {game.players[1].hand} with score {game.players[1].score}")
    
if __name__ == "__main__":
    main()

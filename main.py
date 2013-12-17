from monopyly import *

# True to play a tournament, False to play a single game
# with selected players...
play_tournament = True

# We find the collection of AIs from the AIs folder...
ais = load_ais()

if play_tournament:
    # We play a tournament. This plays all the permutations of
    # AIs against each other.

    # Logging at INFO_PLUS level shows game results, but does not
    # show verbose  information...
    Logger.add_handler(ConsoleLogHandler(Logger.INFO_PLUS))

    # We set up and play a tournament...
    tournament = Tournament(player_ais=ais, max_players_per_game=4, number_of_rounds=100)
    results = tournament.play()
    print(results)
else:
    # We play a single game with selected players.
    #
    # This can be useful for testing your AI in a single game without
    # having to play a full multi-player tournament.
    #
    # To test with your own players, change the AI selections below.

    # Logging at INFO level shows verbose information about each
    # turn in the game...
    Logger.add_handler(ConsoleLogHandler(Logger.INFO))

    # We select specific AIs from the ones loaded...
    sophie_ai = next(ai for ai in ais if ai.get_name() == "Sophie")
    generous_daddy_ai = next(ai for ai in ais if ai.get_name() == "Generous Daddy")
    mean_daddy_ai = next(ai for ai in ais if ai.get_name() == "Mean Daddy")

    # We set up and play a single game...
    game = Game()
    game.add_player(sophie_ai)
    game.add_player(generous_daddy_ai)
    game.add_player(mean_daddy_ai)
    game.play_game()




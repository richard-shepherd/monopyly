from monopyly import *

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--ai_dir",
                    default="AIs")

args = parser.parse_args()

# True to play a tournament, False to play a single game
# with selected players...
play_tournament = True

# We find the collection of AIs from the AIs folder...
ais = load_ais(args.ai_dir)

if play_tournament:
    # We play a tournament. This plays all the permutations of
    # AIs against each other.

    # Logging at INFO_PLUS level shows game results, but does not
    # show verbose information...
    Logger.add_handler(ConsoleLogHandler(Logger.INFO_PLUS))
    Logger.add_handler(FileLogHandler("tournament.log", Logger.INFO_PLUS))
    Logger.log("Number of AIs: {0}".format(len(ais)), Logger.INFO_PLUS)

    # We set up and play a tournament...
    tournament = Tournament(
        player_ais=ais,
        min_players_per_game=4,
        max_players_per_game=4,
        number_of_rounds=100,
        maximum_games=35000,
        permutations_or_combinations=Tournament.PERMUTATIONS)

    # Sends updates to the C# GUI...
    #tournament.messaging_server = MessagingServer(update_every_n_turns=10, sleep_between_turns_seconds=0.0)

    # We play the tournament...
    tournament.play()
    tournament.log_results()

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




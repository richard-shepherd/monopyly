from monopyly import *


# We find the collection of AIs from the AIs folder...
ais = load_ais()

# Playing a tournament
# --------------------
# We play a tournament. This plays all the permutations of
# AIs against each other...
# Logger.add_handler(ConsoleLogHandler(Logger.INFO_PLUS))
# tournament = Tournament(player_ais=ais, max_players_per_game=4, number_of_rounds=100)
# results = tournament.play()
# print(results)


# Playing a game with specific players
# ------------------------------------
# This can be useful for testing your AI in a single game without
# having to play a full multi-player tournament.
#
# To play a game with specific players you should:
# - Comment out the tournament section above.
# - Uncomment the code below and adapt it to select the players you want.
#
# Note that logging at INFO level gives a much more verbose description of the game.
Logger.add_handler(ConsoleLogHandler(Logger.INFO))
sophie_ai = next(ai for ai in ais if ai.get_name() == "Sophie")
generous_daddy_ai = next(ai for ai in ais if ai.get_name() == "Generous Daddy")
mean_daddy_ai = next(ai for ai in ais if ai.get_name() == "Mean Daddy")
game = Game()
game.add_player(sophie_ai)
game.add_player(generous_daddy_ai)
game.add_player(mean_daddy_ai)
game.play_game()




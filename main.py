from monopyly import *

# We set up the logger...
Logger.add_handler(ConsoleLogHandler(Logger.INFO))

# We find the collection of AIs from the AIs folder...
ais = load_ais()

# We play a tournament. This plays all the permutations of players
# against each other...
tournament = Tournament(player_ais=ais, max_players_per_game=4, number_of_rounds=1)
results = tournament.play()
print(results)



from monopyly import *


# We set up the logger...
Logger.add_handler(ConsoleLogHandler(Logger.INFO_PLUS))

# We play a tournament. This plays all the permutations of players
# against each other...
tournament = Tournament(
    player_ais=[SophieAI(), GenerousDaddyAI(), PlayerAIBase()],
    max_players_per_game=4,
    number_of_rounds=100)
results = tournament.play()
print(results)



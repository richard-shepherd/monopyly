from monopyly import *

# TODO: test that events are raised to the AIs, e.g. start of turn etc

# TODO: All calls to the AI should be surrounded with try...catch

# TODO: What do we do if the AI passes back an unexpected type of object?
# We need to avoid the game blowing up.
# Look at: https://pypi.python.org/pypi/typecheck
# OR: maybe this is just caught with the try-catch thing.

# TODO: graphs of cash and 'net worth'

# TODO: code tournaments

# TODO: auto-discovery of AIs

# We set up the logger...
Logger.add_handler(ConsoleLogHandler(Logger.WARNING))

# We play a game with some sample AIs...
results = dict()
for i in range(1000):
    game = Game()
    game.add_player(SophieAI())
    game.add_player(GenerousDaddyAI())
    game.play_game()

    winner = game.winner
    if not winner:
        print("Game {0} was drawn".format(i))
    else:
        print("Winner of game {0} was {1}".format(i, winner.name))
        if winner.name not in results:
            results[winner.name] = 1
        else:
            results[winner.name] += 1

print(results)


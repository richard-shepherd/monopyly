from monopyly import Board

# TODO: build a logging mechanism so that we can see all the events.

# TODO: test that events are raised to the AIs

# TODO: All calls to the AI should be surrounded with try...catch

# TODO: What do we do if the AI passes back an unexpected type of object?
# We need to avoid the game blowing up.
# Look at: https://pypi.python.org/pypi/typecheck
# OR: maybe this is just caught with the try-catch thing.


if(__name__ == "__main__"):
    board = Board()
    a = 99

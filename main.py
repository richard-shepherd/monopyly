from monopyly import Board

# TODO: build a logging mechanism so that we can see all the events.

# TODO: test that events are raised to the AIs

# TODO: All calls to the AI should be surrounded with try...catch

# TODO: What do we do if the AI passes back an unexpected type of object?
# We need to avoid the game blowing up.
# Look at: https://pypi.python.org/pypi/typecheck

# TODO: Avoid giving money and taking money in the same "event" if possible
# e.g. when buying houses, mortgaging etc.
# This could confuse the AIs.
# Instead of acting on the real objects and then rolling back, the code should
# 'simulate' the outcome and not allow it if it looks bad. But should only do
# the real transaction once.
# Maybe this just needs doing for events where the player raises cash.
# So we don't give and then take again, as this may be happening when they
# need cash, and could result in some sort of loop.

if(__name__ == "__main__"):
    board = Board()
    a = 99

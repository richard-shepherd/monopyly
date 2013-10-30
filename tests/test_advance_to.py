from monopyly import *
from testing_utils import *


def test_advance_to():
    '''
    Tests that the "Advance to..." cards work as expected, including
    testing collecting £200 for passing Go.
    '''
    # We set up a game with a single player...
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    # We put the player on square 17 (Community Chest) and
    # simulate Advance to Free Parking...
    player.state.square = 17
    advance_to_free_parking = AdvanceTo(Square.Name.FREE_PARKING)
    advance_to_free_parking.play(game, player)

    # The player should now be at Free Parking, with no extra money...
    assert player.state.square == 20
    assert player.state.cash == 1500

    # If we advance to Free Parking again, nothing should happen
    # (as we are already there)...
    advance_to_free_parking.play(game, player)
    assert player.state.square == 20
    assert player.state.cash == 1500

    # We start at Chance (position 22) and advance to Free Parking.
    # This takes us past Go, so we should have an extra £200...
    player.state.square = 22
    advance_to_free_parking.play(game, player)
    assert player.state.square == 20
    assert player.state.cash == 1700

    # Advancing to Go should give us an extra £200...
    advance_to_go = AdvanceTo(Square.Name.GO)
    advance_to_go.play(game, player)
    assert player.state.square == 0
    assert player.state.cash == 1900



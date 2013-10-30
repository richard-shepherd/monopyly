from monopyly import *
from testing_utils import *


def test_owned_sets():
    '''
    Tests that we find which sets are owned correctly.
    '''
    # We set up a game with two players...
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())
    player2 = game.add_player(DefaultPlayerAI())

    # We give the players some properties. Some have whole sets
    # and some do not...

    # Player 0...
    game.give_property_to_player(player0, Square.Name.OLD_KENT_ROAD)
    game.give_property_to_player(player0, Square.Name.WHITECHAPEL_ROAD)
    game.give_property_to_player(player0, Square.Name.EUSTON_ROAD)

    # Player 1...
    game.give_property_to_player(player1, Square.Name.THE_ANGEL_ISLINGTON)
    game.give_property_to_player(player1, Square.Name.PENTONVILLE_ROAD)

    # Player 2...
    game.give_property_to_player(player2, Square.Name.BOW_STREET)
    game.give_property_to_player(player2, Square.Name.MARLBOROUGH_STREET)
    game.give_property_to_player(player2, Square.Name.VINE_STREET)
    game.give_property_to_player(player2, Square.Name.PARK_LANE)
    game.give_property_to_player(player2, Square.Name.MAYFAIR)
    game.give_property_to_player(player2, Square.Name.TRAFALGAR_SQUARE)
    game.give_property_to_player(player2, Square.Name.COVENTRY_STREET)

    # We find the sets...
    owned_sets = game.state.board.get_owned_sets()

    # Player 0...
    assert 0 in owned_sets
    player0_sets = owned_sets[0]
    assert len(player0_sets) == 1
    assert Property.Set.BROWN in player0_sets

    # Player 1...
    assert 1 not in owned_sets

    # Player 2...
    assert 2 in owned_sets
    player2_sets = owned_sets[2]
    assert len(player2_sets) == 2
    assert Property.Set.ORANGE in player2_sets
    assert Property.Set.DARK_BLUE in player2_sets



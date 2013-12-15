from monopyly import *
from testing_utils import *


def test_owned_sets():
    '''
    Tests that we find which sets are owned correctly.
    '''
    # We set up a game with two players...
    game = Game()
    board = game.state.board
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

    game.give_property_to_player(player1, Square.Name.PALL_MALL)
    game.give_property_to_player(player1, Square.Name.WHITEHALL)
    game.give_property_to_player(player1, Square.Name.NORTHUMBERLAND_AVENUE)
    board.get_square_by_name(Square.Name.PALL_MALL).is_mortgaged = True

    # Player 2...
    game.give_property_to_player(player2, Square.Name.BOW_STREET)
    game.give_property_to_player(player2, Square.Name.MARLBOROUGH_STREET)
    game.give_property_to_player(player2, Square.Name.VINE_STREET)

    game.give_property_to_player(player2, Square.Name.PARK_LANE)
    game.give_property_to_player(player2, Square.Name.MAYFAIR)

    game.give_property_to_player(player2, Square.Name.TRAFALGAR_SQUARE)
    game.give_property_to_player(player2, Square.Name.COVENTRY_STREET)

    # We find the sets...
    game._update_sets()

    # Player 0...
    player0_unmortgaged_sets = player0.state.owned_unmortgaged_sets
    assert len(player0_unmortgaged_sets) == 1
    assert board.get_property_set(PropertySet.BROWN) in player0_unmortgaged_sets

    player0_sets = player0.state.owned_sets
    assert len(player0_sets) == 1
    assert board.get_property_set(PropertySet.BROWN) in player0_sets

    # Player 1...
    player1_unmortgaged_sets = player1.state.owned_unmortgaged_sets
    assert len(player1_unmortgaged_sets) == 0

    player1_sets = player1.state.owned_sets
    assert len(player1_sets) == 1
    assert board.get_property_set(PropertySet.PURPLE) in player1_sets

    # Player 2...
    player2_unmortgaged_sets = player2.state.owned_unmortgaged_sets
    assert len(player2_unmortgaged_sets) == 2
    assert board.get_property_set(PropertySet.ORANGE) in player2_unmortgaged_sets
    assert board.get_property_set(PropertySet.DARK_BLUE) in player2_unmortgaged_sets

    player2_sets = player2.state.owned_sets
    assert len(player2_sets) == 2
    assert board.get_property_set(PropertySet.ORANGE) in player2_sets
    assert board.get_property_set(PropertySet.DARK_BLUE) in player2_sets




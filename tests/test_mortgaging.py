from monopyly import *
from testing_utils import *


class PlayerWhoMortgages(DefaultPlayerAI):
    '''
    A player who mortgages a list of properties.
    '''
    def __init__(self, properties_to_mortgage=[]):
        self.properties_to_mortgage = properties_to_mortgage

    def mortgage_properties(self, game_state, player_state):
        return self.properties_to_mortgage


def test_simple_mortgaging():
    '''
    A player starts off with the orange and green sets and two stations.
    They mortgage Bow Street and one station.

    We check that they get the right amount of money and that their
    property and set-ownership state is correctly updated.
    '''
    game = Game()
    player = game.add_player(PlayerWhoMortgages([Square.Name.BOW_STREET, Square.Name.KINGS_CROSS_STATION]))

    # We give the player the properties...
    square1 = game.give_property_to_player(player, Square.Name.BOW_STREET)
    square2 = game.give_property_to_player(player, Square.Name.MARLBOROUGH_STREET)
    square3 = game.give_property_to_player(player, Square.Name.VINE_STREET)
    square4 = game.give_property_to_player(player, Square.Name.REGENT_STREET)
    square5 = game.give_property_to_player(player, Square.Name.OXFORD_STREET)
    square6 = game.give_property_to_player(player, Square.Name.BOND_STREET)
    square7 = game.give_property_to_player(player, Square.Name.KINGS_CROSS_STATION)
    square8 = game.give_property_to_player(player, Square.Name.MARYLEBONE_STATION)

    # Before mortgaging, we do a quick double-check that the player
    # has the properties and sets as expected...
    assert len(player.state.property_indexes) == 8
    assert len(player.state.owned_sets) == 2
    assert Property.Set.ORANGE in player.state.owned_sets
    assert Property.Set.GREEN in player.state.owned_sets

    # We check that none of the properties are mortgaged...
    assert square1.is_mortgaged is False
    assert square2.is_mortgaged is False
    assert square3.is_mortgaged is False
    assert square4.is_mortgaged is False
    assert square5.is_mortgaged is False
    assert square6.is_mortgaged is False
    assert square7.is_mortgaged is False
    assert square8.is_mortgaged is False

    # The player starts on Liverpool Street Station and rolls a 3
    # to end up on Super Tax. (We need a payment of some kind to
    # trigger the mortgaging process.)
    player.state.square = 35
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should have received £90 + £100 and paid £100...
    assert player.state.cash == 1590
    assert len(player.state.property_indexes) == 8
    assert len(player.state.owned_sets) == 1
    assert Property.Set.GREEN in player.state.owned_sets

    # We check that Bow Street and Kings Cross are mortgaged...
    assert square1.is_mortgaged is True
    assert square2.is_mortgaged is False
    assert square3.is_mortgaged is False
    assert square4.is_mortgaged is False
    assert square5.is_mortgaged is False
    assert square6.is_mortgaged is False
    assert square7.is_mortgaged is True
    assert square8.is_mortgaged is False


def test_mortgaging_a_non_property_square():
    '''
    Mortgaging a non-property square should do nothing.
    '''
    game = Game()
    player = game.add_player(PlayerWhoMortgages([Square.Name.FREE_PARKING]))

    # The player starts on Liverpool Street Station and rolls a 3
    # to end up on Super Tax. (We need a payment of some kind to
    # trigger the mortgaging process.)
    player.state.square = 35
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should have received nothing and paid £100...
    assert player.state.cash == 1400
    assert len(player.state.property_indexes) == 0

def test_mortgaging_a_property_belonging_to_another_player():
    '''
    We should ignore an attempt to mortgage a property belonging
    to another player as well as one not owned at all.
    '''
    game = Game()
    player0 = game.add_player(PlayerWhoMortgages(
        [Square.Name.BOW_STREET, Square.Name.KINGS_CROSS_STATION, Square.Name.BOND_STREET]))
    player1 = game.add_player(DefaultPlayerAI())

    # Player 0 has the orange set...
    square1 = game.give_property_to_player(player0, Square.Name.BOW_STREET)
    square2 = game.give_property_to_player(player0, Square.Name.MARLBOROUGH_STREET)
    square3 = game.give_property_to_player(player0, Square.Name.VINE_STREET)

    # Player 1 has the green set...
    square4 = game.give_property_to_player(player1, Square.Name.REGENT_STREET)
    square5 = game.give_property_to_player(player1, Square.Name.OXFORD_STREET)
    square6 = game.give_property_to_player(player1, Square.Name.BOND_STREET)

    # The player starts on Liverpool Street Station and rolls a 3
    # to end up on Super Tax. (We need a payment of some kind to
    # trigger the mortgaging process.)
    player0.state.square = 35
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player0)

    # Player 0 should have received £90 and paid £100...
    assert player0.state.cash == 1490
    assert len(player0.state.property_indexes) == 3
    assert len(player0.state.owned_sets) == 0

    # Player 1 should still have all his properties...
    assert len(player1.state.property_indexes) == 3
    assert len(player1.state.owned_sets) == 1
    assert Property.Set.GREEN in player1.state.owned_sets

    # We check that Bow Street is mortgaged (and Bond Street is not)...
    assert square1.is_mortgaged is True
    assert square2.is_mortgaged is False
    assert square3.is_mortgaged is False
    assert square4.is_mortgaged is False
    assert square5.is_mortgaged is False
    assert square6.is_mortgaged is False

    # We check that Kings Cross is not mortgaged (as player 0 did not own it)...
    kings_cross = game.state.board.get_square_by_name(Square.Name.KINGS_CROSS_STATION)
    assert kings_cross.is_mortgaged is False


def test_mortgage_property_with_houses():
    '''
    You can't mortgage a property with houses on it.
    '''
    game = Game()
    player = game.add_player(PlayerWhoMortgages([Square.Name.BOW_STREET]))

    # We give the player Bow Street and put some houses on it...
    bow_street = game.give_property_to_player(player, Square.Name.BOW_STREET)
    bow_street.number_of_houses = 3

    # The player starts on Liverpool Street Station and rolls a 3
    # to end up on Super Tax. (We need a payment of some kind to
    # trigger the mortgaging process.)
    player.state.square = 35
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should have received nothing and paid £100.
    # Bow Street should not be mortgaged...
    assert player.state.cash == 1400
    assert bow_street.is_mortgaged is False



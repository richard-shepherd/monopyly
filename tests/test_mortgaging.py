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
    game.give_property_to_player(player, Square.Name.BOW_STREET)
    game.give_property_to_player(player, Square.Name.MARLBOROUGH_STREET)
    game.give_property_to_player(player, Square.Name.VINE_STREET)
    game.give_property_to_player(player, Square.Name.REGENT_STREET)
    game.give_property_to_player(player, Square.Name.OXFORD_STREET)
    game.give_property_to_player(player, Square.Name.BOND_STREET)
    game.give_property_to_player(player, Square.Name.KINGS_CROSS_STATION)
    game.give_property_to_player(player, Square.Name.MARYLEBONE_STATION)

    # Before mortgaging, we do a quick double-check that the player
    # has the properties and sets as expected...
    assert len(player.state.property_indexes) == 8
    assert len(player.state.owned_sets) == 2
    assert Property.Set.ORANGE in player.state.owned_sets
    assert Property.Set.GREEN in player.state.owned_sets

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


# TODO: trying to mortgage a property you do not own

# TODO: trying to mortgage a non-property square

# TODO: trying to mortgage a property with houses on

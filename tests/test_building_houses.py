# TODO: unbalanced building

# TODO: player builds on unowned properties

# TODO: player builds on partially mortgaged set

# TODO: player builds more than 5 houses

from monopyly import *
from testing_utils import *


class PlayerWhoBuildsHouses(DefaultPlayerAI):
    '''
    A player who builds houses.
    '''
    def __init__(self, build_instructions=None):
        if not build_instructions:
            build_instructions = []
        self.build_instructions = build_instructions

    def build_houses(self, game_state, player_state):
        return self.build_instructions


def test_simple_house_building():
    '''
    Builds two houses on each of the red set.
    '''
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 2),
        (Square.Name.FLEET_STREET, 2),
        (Square.Name.TRAFALGAR_SQUARE, 2)]))

    # We give the player the red set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # The player should have built houses on the three properties...
    assert strand.number_of_houses == 2
    assert fleet_street.number_of_houses == 2
    assert trafalgar_square.number_of_houses == 2

    # We check the player paid the right money, 6 * £150 = £900
    assert player.state.cash == 600


def test_building_on_incomplete_set():
    '''
    You cannot build houses unless you own the whole set.
    '''
    # The player will try to build a house on two properties
    # of the red set, without owning the whole set.
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 1),
        (Square.Name.FLEET_STREET, 1)]))

    # We give the player two properties from the red set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # The player should not have any houses...
    assert strand.number_of_houses == 0
    assert fleet_street.number_of_houses == 0

    # No money should have been taken...
    assert player.state.cash == 1500


def test_building_not_enough_money():
    '''
    Builds two houses on each of the red set, but the player
    does not have enough money
    '''
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 2),
        (Square.Name.FLEET_STREET, 2),
        (Square.Name.TRAFALGAR_SQUARE, 2)]))

    # We give the player the red set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)

    # The player does not have enough money to build the houses...
    player.state.cash = 800

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # No houses should have been built...
    assert strand.number_of_houses == 0
    assert fleet_street.number_of_houses == 0
    assert trafalgar_square.number_of_houses == 0

    # No money should have been taken...
    assert player.state.cash == 800


def test_builds_then_mortgages():
    '''
    The player wants to build houses on the red set, but mortgages
    one of the properties to pay for it. The houses should not be
    built in this case.
    '''
    class PlayerWhoBuildsAndMortgages(DefaultPlayerAI):
        def build_houses(self, game_state, player_state):
            return [(Square.Name.STRAND, 2), (Square.Name.FLEET_STREET, 2), (Square.Name.TRAFALGAR_SQUARE, 2)]

        def mortgage_properties(self, game_state, player_state):
            return [Square.Name.TRAFALGAR_SQUARE]

    game = Game()
    player = game.add_player(PlayerWhoBuildsAndMortgages())

    # We give the player the red set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # No houses should have been built...
    assert strand.number_of_houses == 0
    assert fleet_street.number_of_houses == 0
    assert trafalgar_square.number_of_houses == 0

    # The player should have the money from mortgaging Trafalgar Square...
    assert player.state.cash == 1620




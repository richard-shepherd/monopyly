# TODO: unbalanced building

# TODO: player builds on unowned properties

# TODO: player builds on partially mortgaged set

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
    Builds two houses on each of the red set and one each on the brown set.
    '''
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 2),
        (Square.Name.FLEET_STREET, 2),
        (Square.Name.TRAFALGAR_SQUARE, 2),
        (Square.Name.OLD_KENT_ROAD, 1),
        (Square.Name.WHITECHAPEL_ROAD, 1)]))

    # We give the player the red set and the brown set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)
    old_kent_road = game.give_property_to_player(player, Square.Name.OLD_KENT_ROAD)
    whitechapel_road = game.give_property_to_player(player, Square.Name.WHITECHAPEL_ROAD)

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # The player should have built houses on the three properties...
    assert strand.number_of_houses == 2
    assert fleet_street.number_of_houses == 2
    assert trafalgar_square.number_of_houses == 2
    assert old_kent_road.number_of_houses == 1
    assert whitechapel_road.number_of_houses == 1

    # We check the player paid the right money, 6 * £150 + 2 * £50 = £1000
    assert player.state.cash == 500


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
    The player wants to build houses on the red set, but tries to
    mortgage one of the properties to pay for it.

    If they have enough money, the houses will be built anyway, but
    the property will not be mortgaged.

    If they do not have enough money, the houses will not be built.
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

    # The player does not have enough money to build the
    # houses without mortgaging...
    player.state.cash = 800

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # No houses should have been built and the mortgage does not happen.
    # No money should have been taken...
    assert strand.number_of_houses == 0
    assert fleet_street.number_of_houses == 0
    assert trafalgar_square.number_of_houses == 0
    assert trafalgar_square.is_mortgaged is False
    assert player.state.cash == 800

    # We try again. This time, the player does have enough money...
    player.state.cash = 925
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # The houses should have been built, but Trafalgar Square
    # will not be mortgaged...
    assert strand.number_of_houses == 2
    assert fleet_street.number_of_houses == 2
    assert trafalgar_square.number_of_houses == 2
    assert trafalgar_square.is_mortgaged is False
    assert player.state.cash == 25


def test_build_more_than_five_houses():
    '''
    Builds six houses on each of the red set. This is not allowed.
    '''
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 6),
        (Square.Name.FLEET_STREET, 6),
        (Square.Name.TRAFALGAR_SQUARE, 6)]))

    # We give the player the red set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)

    # We give the player enough money to buy 6 houses on each...
    player.state.cash = 3000

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
    assert player.state.cash == 3000


def test_building_a_negative_number_of_houses():
    '''
    You should not be allowed to build a negative number of houses.
    This should not be a sneaky way of selling houses back at full price!
    '''
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.PARK_LANE, -2),
        (Square.Name.MAYFAIR, -2)]))

    # We give the player the dark-blue set, each with four houses...
    park_lane = game.give_property_to_player(player, Square.Name.PARK_LANE)
    mayfair = game.give_property_to_player(player, Square.Name.MAYFAIR)
    park_lane.number_of_houses = 4
    mayfair.number_of_houses = 4

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # No houses should have been built (or un-built)...
    assert park_lane.number_of_houses == 4
    assert mayfair.number_of_houses == 4

    # The player should have the money they started with...
    assert player.state.cash == 1500


def test_unbalanced_house_building():
    '''
    Unbalanced house building is not allowed.
    '''
    # The player is trying to build 4 houses on Trafalgar Square, but
    # only two houses on the other red squares...
    game = Game()
    player = game.add_player(PlayerWhoBuildsHouses([
        (Square.Name.STRAND, 2),
        (Square.Name.FLEET_STREET, 2),
        (Square.Name.TRAFALGAR_SQUARE, 4),
        (Square.Name.OLD_KENT_ROAD, 1),
        (Square.Name.WHITECHAPEL_ROAD, 1)]))

    # We give the player the red set and the brown set...
    strand = game.give_property_to_player(player, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player, Square.Name.FLEET_STREET)
    trafalgar_square = game.give_property_to_player(player, Square.Name.TRAFALGAR_SQUARE)
    old_kent_road = game.give_property_to_player(player, Square.Name.OLD_KENT_ROAD)
    whitechapel_road = game.give_property_to_player(player, Square.Name.WHITECHAPEL_ROAD)

    # We need to play a turn to initiate house building. We play a
    # neutral turn: Marylebone -> Free parking.
    player.state.square = 15
    game.dice = MockDice([(4, 1)])
    game.play_one_turn(player)

    # No houses should have been built and no money taken...
    assert strand.number_of_houses == 0
    assert fleet_street.number_of_houses == 0
    assert trafalgar_square.number_of_houses == 0
    assert old_kent_road.number_of_houses == 0
    assert whitechapel_road.number_of_houses == 0
    assert player.state.cash == 1500

# TODO: simple house building

# TODO: unbalanced building

# TODO: player doesn't have enough money

# TODO: player builds on unowned properties

# TODO: player builds on incomplete set

# TODO: player builds on partially mortgaged set

# TODO: player builds, then mortgages properties

# TODO: player builds more than 5 houses

from monopyly import *
from testing_utils import *


class PlayerWhoBuildsHouses(DefaultPlayerAI):
    '''
    A player who builds houses.
    '''
    def __init__(self, build_instructions=[]):
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

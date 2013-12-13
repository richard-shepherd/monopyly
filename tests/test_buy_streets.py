from monopyly import *
from testing_utils import *


class PlayerWhoBuysEverything(DefaultPlayerAI):
    '''
    A player who buys everything.
    '''
    def landed_on_unowned_property(self, game_state, player, property):
        return PlayerAIBase.Action.BUY


def test_buy_streets():
    '''
    Tests buying the orange set, with a player who buys everything
    they land on.
    '''
    # We set up the game with a player who buys everything...
    game = Game()
    player = game.add_player(PlayerWhoBuysEverything())

    # The player starts at Just Visiting, and rolls a (3, 3) to land on Bow Street,
    # then (1, 1) to land on Marlborough Street, then (0, 1) to land on Vine Street...
    player.state.square = 10
    game.dice = MockDice([(3, 3), (1, 1), (0, 1)])
    game.play_one_turn(player)

    board = game.state.board
    bow_street = board.get_square_by_name(Square.Name.BOW_STREET)
    marlborough_street = board.get_square_by_name(Square.Name.MARLBOROUGH_STREET)
    vine_street = board.get_square_by_name(Square.Name.VINE_STREET)

    # The player should have bought the orange set...
    assert len(player.state.properties) == 3
    assert bow_street in player.state.properties
    assert marlborough_street in player.state.properties
    assert vine_street in player.state.properties
    assert len(player.state.owned_sets) == 1
    assert board.get_property_set(PropertySet.ORANGE) in player.state.owned_sets

    # The player should have paid the money...
    assert player.state.cash == 940

    # The squares should know their owner...
    assert bow_street.owner is player
    assert marlborough_street.owner is player
    assert vine_street.owner is player


def test_buy_streets_not_enough_money():
    '''
    As above, except that the player does not have enough money
    to buy all three properties.
    '''
    # We set up the game with a player who buys everything...
    game = Game()
    player = game.add_player(PlayerWhoBuysEverything())

    # The player starts at Just Visiting, and rolls a (3, 3) to land on Bow Street,
    # then (1, 1) to land on Marlborough Street, then (0, 1) to land on Vine Street...
    player.state.cash = 500
    player.state.square = 10
    game.dice = MockDice([(3, 3), (1, 1), (0, 1)])
    game.play_one_turn(player)

    board = game.state.board
    bow_street = board.get_square_by_name(Square.Name.BOW_STREET)
    marlborough_street = board.get_square_by_name(Square.Name.MARLBOROUGH_STREET)
    vine_street = board.get_square_by_name(Square.Name.VINE_STREET)

    # The player should have bought only the first two properties...
    assert len(player.state.properties) == 2
    assert bow_street in player.state.properties
    assert marlborough_street in player.state.properties
    assert len(player.state.owned_sets) == 0

    # The player should have paid the money...
    assert player.state.cash == 140

    # The squares should know their owner...
    board = game.state.board
    assert bow_street.owner is player
    assert marlborough_street.owner is player
    assert vine_street.owner is None





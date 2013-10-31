from monopyly import *
from testing_utils import *


class PlayerWhoBuysEverything(DefaultPlayerAI):
    '''
    A player who buys everything.
    '''
    def landed_on_unowned_property(self, game_state, player_state, property_name, price):
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

    # The player should have bought the orange set...
    assert len(player.state.property_indexes) == 3
    assert 16 in player.state.property_indexes
    assert 18 in player.state.property_indexes
    assert 19 in player.state.property_indexes
    assert len(player.state.owned_sets) == 1
    assert Property.Set.ORANGE in player.state.owned_sets

    # The player should have paid the money...
    assert player.state.cash == 940

    # The squares should know their owner...
    player_number = player.state.player_number
    board = game.state.board
    assert board.get_square_by_name(Square.Name.BOW_STREET).owner_player_number == player_number
    assert board.get_square_by_name(Square.Name.MARLBOROUGH_STREET).owner_player_number == player_number
    assert board.get_square_by_name(Square.Name.VINE_STREET).owner_player_number == player_number


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

    # The player should have bought only the first two properties...
    assert len(player.state.property_indexes) == 2
    assert 16 in player.state.property_indexes
    assert 18 in player.state.property_indexes
    assert len(player.state.owned_sets) == 0

    # The player should have paid the money...
    assert player.state.cash == 140

    # The squares should know their owner...
    player_number = player.state.player_number
    board = game.state.board
    assert board.get_square_by_name(Square.Name.BOW_STREET).owner_player_number == player_number
    assert board.get_square_by_name(Square.Name.MARLBOROUGH_STREET).owner_player_number == player_number
    assert board.get_square_by_name(Square.Name.VINE_STREET).owner_player_number == Property.NOT_OWNED





# TODO: player buys out of jail on turn 1

# TODO: player plays get out of jail free, has two cards

# TODO: player plays GOOJF, but doesn't have the card.

# TODO: player rolls 7 and gets a CommunityChest card to go back to jail


from monopyly import *
from testing_utils import *


class PlayerWhoGetsOutOfJail(DefaultPlayerAI):
    '''
    A player who performs the given action when in jail.
    '''
    def __init__(self, action):
        self.action = action

    def set_action(self, action):
        self.action = action

    def get_out_of_jail(self, player_state):
        return self.action


def test_has_to_pay_on_third_turn():
    '''
    The player fails to roll doubles for the three turns inside
    and must pay £50.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.STAY_IN_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player doesn't roll doubles in the next three turns...
    game.dice = MockDice([(2, 3), (1, 4), (6, 4)])

    # We play the first turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 1

    # We play the second turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 2

    # We play the third turn. The player should have been forced
    # to pay their way out...
    game.play_one_turn(player)
    assert player.state.square == 20
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450


def test_roll_doubles_on_third_turn():
    '''
    Tests that rolling doubles on the third turn in jail gets you
    out of jail without paying (and that you don't get a turn afterwards).
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.STAY_IN_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player rolls double on the third turn...
    game.dice = MockDice([(2, 3), (1, 4), (5, 5), (1, 2)])

    # We play the first turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 1

    # We play the second turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 2

    # We play the third turn. The player rolls doubles to get out...
    game.play_one_turn(player)
    assert player.state.square == 20
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1500


def test_buy_way_out():
    '''
    The player buys their way out on the first turn.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player buys their way out then rolls 8...
    game.dice = MockDice([(3, 5)])

    # The player should have paid £50 and be on Marlborough Street...
    game.play_one_turn(player)
    assert player.state.square == 18
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450



# TODO: player stays in jail: turn 1 and 2 has to pay on turn 3

# TODO: player rolls doubles on third turn.

# TODO: player buys out of jail on turn 1

# TODO: player rolls doubles to get out. Doesn't roll again.

# TODO: player plays get out of jail free, has two cards

# TODO: player plays GOOJF, but doesn't have the card.
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

    # We player the third turn. The player should have been forced
    # to pay their way out...
    game.play_one_turn(player)
    assert player.state.square == 20
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450



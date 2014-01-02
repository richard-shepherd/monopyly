from monopyly import *
from testing_utils import *
import time


class PlayerWhoThinksTooLong(DefaultPlayerAI):
    '''
    A player who thinks for one second whether to buy property.
    '''
    def __init__(self):
        self.out_of_time = False

    def landed_on_unowned_property(self, game_state, player, property):
        time.sleep(1)
        return PlayerAIBase.Action.DO_NOT_BUY

    def player_ran_out_of_time(self, player):
        self.out_of_time = True


def test_enough_time_remaining():
    '''
    Both players have enough time for their next turn.
    '''
    game = Game()
    slow_player = game.add_player(PlayerWhoThinksTooLong())
    fast_player = game.add_player(DefaultPlayerAI())

    # We play one round...
    slow_player.state.ai_processing_seconds_remaining = 10.0
    fast_player.state.ai_processing_seconds_remaining = 10.0
    game.dice = MockDice([(2, 4), (5, 3)])
    game.play_one_round()

    # Both players should still be in the game...
    assert slow_player in game.state.players
    assert slow_player.ai.out_of_time is False
    assert fast_player in game.state.players


def test_player_runs_out_of_time():
    '''
    One of the players runs out of time.
    '''
    game = Game()
    slow_player = game.add_player(PlayerWhoThinksTooLong())
    fast_player = game.add_player(DefaultPlayerAI())

    # We play one round...
    slow_player.state.ai_processing_seconds_remaining = 0.5
    fast_player.state.ai_processing_seconds_remaining = 10.0
    game.dice = MockDice([(2, 4), (5, 3)])
    game.play_game()

    # Both players should still be in the game...
    assert slow_player in game.state.bankrupt_players
    assert slow_player.ai.out_of_time is True
    assert fast_player in game.state.players

    # The fast-player should have won the game...
    assert game.winner is fast_player

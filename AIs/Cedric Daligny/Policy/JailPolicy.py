__author__ = 'Cedric'

import random
from monopyly import *

class JailPolicy(object):
    '''
OutOfJailInformation
                threshold_random_exit
                max_round_in_jail # no limit is 500
                threshold_free_square
    '''
    def __init__(self,threshold,max_round,free_square):
        '''
        ctor
        '''
        self.threshold_random_exit = threshold
        self.max_round = max_round
        self.min_free_square = free_square

    def compute(self, ia, game_state, player):
        '''
        Called in the player's turn, before the dice are rolled, if the player
        is in jail.

        There are three possible return values:
        PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        PlayerAIBase.Action.STAY_IN_JAIL

        Buying your way out of jail will cost £50.

        The default action is STAY_IN_JAIL.
        '''
        if random.random() < self.threshold_random_exit or \
           player.state.number_of_turns_in_jail > self.max_round or \
           self.free_square_from(game_state) >= self.min_free_square:
            if player.state.number_of_get_out_of_jail_free_cards > 0:
                return PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
            return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        return PlayerAIBase.Action.STAY_IN_JAIL

    def free_square_from(self,game_state):
        nb_occupied_square = 0
        for player in game_state.players:
            nb_occupied_square += len(player.state.properties)
        return 40 - nb_occupied_square
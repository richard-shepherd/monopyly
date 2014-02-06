__author__ = 'Cedric'

from monopyly import *

class BuyingPolicy(object):
    def __init__(self,threshold_buy_at_any_cost,keep_cash):
        '''
        ctor
        '''
        self.threshold = threshold_buy_at_any_cost
        self.keep_cash = keep_cash

    def compute(self, ai, game_state, player, property):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        for properties in ai.properties_weight:
            if properties[0] == property.name:
                if properties[1] > self.threshold:
                    return PlayerAIBase.Action.BUY
                elif player.state.cash > self.keep_cash:
                    return PlayerAIBase.Action.BUY
        return PlayerAIBase.Action.DO_NOT_BUY
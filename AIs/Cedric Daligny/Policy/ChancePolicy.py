__author__ = 'Cedric'

import random
from monopyly import *

class ChancePolicy(object):
    def __init__(self,threshold):
        '''
        ctor
        '''
        self.threshold = threshold
    def compute(self):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
        if random.random() < self.threshold:
            return PlayerAIBase.Action.TAKE_A_CHANCE
        return PlayerAIBase.Action.PAY_TEN_POUND_FINE

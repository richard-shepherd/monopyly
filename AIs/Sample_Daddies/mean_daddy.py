from monopyly import *
from .generous_daddy import GenerousDaddyAI
import random


class MeanDaddyAI(GenerousDaddyAI):
    '''
    Similar to GenerousDaddyAI (which it is derived from)
    except that it does not accept deals and bids lower in
    auctions.
    '''
    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Mean Daddy"

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        return DealResponse(DealResponse.Action.REJECT)

    def property_offered_for_auction(self, game_state, player, property):
        '''
        We offer the face face plus or minus a random amount.
        '''
        return property.price + random.randint(-100, 50)


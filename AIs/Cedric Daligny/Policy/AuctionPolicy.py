__author__ = 'Cedric'

from ..Memory import *
from monopyly import *

class AuctionPolicy(object):
    def __init__(self,memory,threshold_buy_at_any_cost,keep_cash):
        '''
        ctor
        '''
        self.memory = memory
        self.threshold = threshold_buy_at_any_cost
        self.keep_cash = keep_cash

    def compute(self, ai, game_state, player, property):
        '''
        Called when a property is put up for auction.

        Properties are auctioned when a player lands on an unowned square but does
        not want to buy it. All players take part in the auction, including the
        player who landed on the square.

        The property will be sold to the highest bidder using the eBay rule,
        ie, for £1 more than the second-highest bid.

        Return the amount you bid. To put in a bid this must be a positive integer.
        Zero means that you are not bidding (it does not mean that you are bidding
        zero).

        The default behaviour is not to bid.
        '''
        for properties in ai.properties_weight:
            if properties[0] == property.name:
                if properties[1] > self.threshold:
                    return player.state.cash
                elif player.state.cash > self.keep_cash:
                    return player.state.cash - self.keep_cash
        return 0

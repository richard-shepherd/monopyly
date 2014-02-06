__author__ = 'Cedric'

from monopyly import *

class AuctionMemory(object):
    def __init__(self):
        '''
        ctor
        '''

    def add_auction(self, property, player, amount_paid):
        '''
        Called with the result of an auction. All players receive
        this notification.

        status is either AUCTION_SUCCEEDED or AUCTION_FAILED.

        If the auction succeeded, the property, the player who won
        the auction and the amount they paid are passed to the AI.

        If the auction failed, the player will be None and the
        amount paid will be 0.

        No response is required.
        '''
        pass

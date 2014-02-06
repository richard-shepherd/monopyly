__author__ = 'Cedric'

from monopyly import *

class DealMemory(object):
    def __init__(self):
        '''
        ctor
        '''

    def add_deal(self, deal_result):
        '''
        Called when a deal has successfully completed to let all
        players know the details of the deal which took place.

        deal_result is a DealResult object.

        Note that the cash_transferred_from_proposer_to_proposee in
        the deal_result can be negative if cash was transferred from
        the proposee to the proposer.

        No response is required.
        '''
        pass
from .dividend_of_fifty import DividendOfFifty
from .elected_chairman import ElectedChairman


class ChanceDesk(object):
    '''
    Manages the set of Chance cards.
    '''

    def __init__(self):
        '''
        The 'constructor'
        '''
        self.cards = [DividendOfFifty(),
                      ElectedChairman()]

from .deck import Deck
from .dividend_of_fifty import DividendOfFifty
from .elected_chairman import ElectedChairman
import random


class ChanceDeck(Deck):
    '''
    Manages the set of Chance cards.
    '''

    def __init__(self):
        '''
        The 'constructor'
        '''
        super().__init__()
        self.cards = [DividendOfFifty(),
                      ElectedChairman()]
        random.shuffle(self.cards)


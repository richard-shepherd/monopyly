
class Deck(object):
    '''
    A base class for decks of cards.

    There are derived classes for the Chance and Community Chest decks.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cards = []
        self.index = 0

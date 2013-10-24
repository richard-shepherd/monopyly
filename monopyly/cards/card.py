
class Card(object):
    '''
    A base class for cards.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        # True if the card is in the deck.
        # This can be False for the Get Out Of Jail Free cards when
        # they are owned by a player.
        self.in_deck = True

